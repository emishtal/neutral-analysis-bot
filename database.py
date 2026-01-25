import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица разборов ситуаций
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    
                    -- 8 вопросов
                    situation TEXT,
                    participants TEXT,
                    agreement_type TEXT,
                    agreement_details TEXT,
                    completion_criteria TEXT,
                    what_happened TEXT,
                    evidence TEXT,
                    main_concern TEXT,
                    
                    -- Персонализация (опционально)
                    user_name TEXT,
                    user_age INTEGER,
                    user_gender TEXT,
                    
                    -- Уточнение фактов
                    facts_updated BOOLEAN DEFAULT 0,
                    refinement_text TEXT,
                    
                    -- Результаты
                    tariff TEXT,
                    initial_analysis TEXT,
                    final_analysis TEXT,
                    
                    -- Метаданные
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица платежей (для будущей интеграции с ЮKassa)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    analysis_id INTEGER,
                    amount INTEGER NOT NULL,
                    tariff TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (analysis_id) REFERENCES analyses (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def create_user(self, user_id: int, username: str = None, first_name: str = None):
        """Создать или обновить пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            conn.commit()
    
    def create_analysis(self, user_id: int) -> int:
        """Создать новый разбор ситуации"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analyses (user_id)
                VALUES (?)
            ''', (user_id,))
            conn.commit()
            return cursor.lastrowid
    
    def update_analysis(self, analysis_id: int, **kwargs):
        """Обновить данные разбора"""
        if not kwargs:
            return
        
        # Всегда обновляем updated_at
        kwargs['updated_at'] = datetime.now().isoformat()
        
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [analysis_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE analyses
                SET {fields}
                WHERE id = ?
            ''', values)
            conn.commit()
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Получить данные разбора"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analyses WHERE id = ?
            ''', (analysis_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_latest_analysis(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить последний разбор пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analyses 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_payment(self, user_id: int, analysis_id: int, amount: int, tariff: str) -> int:
        """Создать запись о платеже (для будущей интеграции)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payments (user_id, analysis_id, amount, tariff, status)
                VALUES (?, ?, ?, ?, 'completed')
            ''', (user_id, analysis_id, amount, tariff))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Количество разборов
            cursor.execute('''
                SELECT COUNT(*) FROM analyses WHERE user_id = ?
            ''', (user_id,))
            total_analyses = cursor.fetchone()[0]
            
            # Сумма платежей
            cursor.execute('''
                SELECT SUM(amount) FROM payments 
                WHERE user_id = ? AND status = 'completed'
            ''', (user_id,))
            total_spent = cursor.fetchone()[0] or 0
            
            return {
                'total_analyses': total_analyses,
                'total_spent': total_spent
            }
