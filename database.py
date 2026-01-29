"""
Database module с поддержкой анонимизации
Добавлена таблица anonymized_analyses для обезличенных данных
"""

import sqlite3
import json
from datetime import datetime, timedelta
from anonymizer import create_anonymized_record


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица анализов (исходные данные - удаляются через 7 дней)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                situation TEXT,
                participants TEXT,
                agreement_type TEXT,
                agreement_details TEXT,
                completion_criteria TEXT,
                what_happened TEXT,
                evidence TEXT,
                main_concern TEXT,
                refinement_text TEXT,
                initial_analysis TEXT,
                final_analysis TEXT,
                tariff TEXT DEFAULT 'basic',
                facts_updated BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                anonymized_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # НОВАЯ ТАБЛИЦА: Анонимизированные анализы (хранятся вечно)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anonymized_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_month TEXT NOT NULL,
                conflict_type TEXT,
                key_word TEXT,
                situation_template TEXT,
                tariff TEXT,
                quality_metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица платежей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                analysis_id INTEGER,
                amount INTEGER NOT NULL,
                tariff TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ... (все остальные методы остаются без изменений)
    
    def create_user(self, telegram_id, username=None, first_name=None):
        """Создание или обновление пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (telegram_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def create_analysis(self, user_id):
        """Создание нового анализа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analyses (user_id) VALUES (?)
        ''', (user_id,))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def update_analysis(self, analysis_id, **kwargs):
        """Обновление анализа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Формируем SET часть запроса
        set_parts = []
        values = []
        
        for key, value in kwargs.items():
            set_parts.append(f"{key} = ?")
            values.append(value)
        
        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE analyses SET {', '.join(set_parts)} WHERE id = ?"
        values.append(analysis_id)
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def get_analysis(self, analysis_id):
        """Получение анализа по ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def create_payment(self, user_id, analysis_id, amount, tariff):
        """Создание записи о платеже"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payments (user_id, analysis_id, amount, tariff)
            VALUES (?, ?, ?, ?)
        ''', (user_id, analysis_id, amount, tariff))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id):
        """Получение статистики пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_analyses
            FROM analyses
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_analyses': result[0] if result else 0
        }
    
    # НОВЫЕ МЕТОДЫ ДЛЯ АНОНИМИЗАЦИИ
    
    def anonymize_and_save(self, analysis_id):
        """
        Создаёт анонимную версию анализа и сохраняет её
        
        Args:
            analysis_id: ID анализа для обезличивания
        
        Returns:
            ID созданной анонимной записи или None
        """
        # Получаем оригинальный анализ
        analysis = self.get_analysis(analysis_id)
        
        if not analysis:
            return None
        
        # Создаём анонимную запись
        anon_data = create_anonymized_record(analysis)
        
        # Сохраняем в БД
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO anonymized_analyses 
            (created_month, conflict_type, key_word, situation_template, tariff, quality_metrics)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            anon_data['created_month'],
            anon_data['conflict_type'],
            anon_data['key_word'],
            anon_data['situation_template'],
            anon_data['tariff'],
            json.dumps(anon_data['quality_metrics'])
        ))
        
        anon_id = cursor.lastrowid
        
        # Помечаем оригинал как обезличенный
        cursor.execute('''
            UPDATE analyses 
            SET anonymized_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (analysis_id,))
        
        conn.commit()
        conn.close()
        
        return anon_id
    
    def cleanup_old_analyses(self, days=7):
        """
        Удаляет анализы старше указанного количества дней
        (только если они уже обезличены)
        
        Args:
            days: Количество дней
        
        Returns:
            Количество удалённых записей
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Удаляем только обезличенные анализы
        cursor.execute('''
            DELETE FROM analyses 
            WHERE created_at < ? 
            AND anonymized_at IS NOT NULL
        ''', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_anonymized_stats(self):
        """Получение статистики по анонимным данным"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общее количество
        cursor.execute('SELECT COUNT(*) FROM anonymized_analyses')
        total = cursor.fetchone()[0]
        
        # По типам конфликтов
        cursor.execute('''
            SELECT conflict_type, COUNT(*) as count
            FROM anonymized_analyses
            GROUP BY conflict_type
            ORDER BY count DESC
        ''')
        by_type = cursor.fetchall()
        
        # По месяцам
        cursor.execute('''
            SELECT created_month, COUNT(*) as count
            FROM anonymized_analyses
            GROUP BY created_month
            ORDER BY created_month DESC
            LIMIT 12
        ''')
        by_month = cursor.fetchall()
        
        # По тарифам
        cursor.execute('''
            SELECT tariff, COUNT(*) as count
            FROM anonymized_analyses
            GROUP BY tariff
        ''')
        by_tariff = cursor.fetchall()
        
        conn.close()
        
        return {
            'total': total,
            'by_type': dict(by_type),
            'by_month': dict(by_month),
            'by_tariff': dict(by_tariff)
        }
