"""
Работа с базой данных
SQLite для хранения пользователей и запросов
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any
from config import Config


class Database:
    """Класс для работы с БД"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self._init_db()
    
    def _get_connection(self):
        """Создать подключение к БД"""
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Инициализация таблиц"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referral_count INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица запросов на анализ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                context TEXT,
                participants TEXT,
                agreement_type TEXT,
                agreement_text TEXT,
                facts TEXT,
                evidence TEXT,
                concern TEXT,
                tariff TEXT,
                price INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица результатов анализа
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                analysis_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES analysis_requests (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: int, username: Optional[str], first_name: str):
        """Создать или обновить пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def create_analysis_request(
        self,
        user_id: int,
        context: str,
        participants: str,
        agreement_type: str,
        agreement_text: str,
        facts: str,
        evidence: str,
        concern: str,
        tariff: str,
        price: int
    ) -> int:
        """Создать запрос на анализ"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_requests (
                user_id, context, participants, agreement_type,
                agreement_text, facts, evidence, concern, tariff, price
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, context, participants, agreement_type,
            agreement_text, facts, evidence, concern, tariff, price
        ))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    def save_analysis_result(self, request_id: int, analysis_text: str):
        """Сохранить результат анализа"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_results (request_id, analysis_text)
            VALUES (?, ?)
        ''', (request_id, analysis_text))
        
        # Обновляем статус запроса
        cursor.execute('''
            UPDATE analysis_requests
            SET status = 'completed'
            WHERE id = ?
        ''', (request_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_requests
            FROM analysis_requests
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_requests': result[0] if result else 0
        }
    
    def increment_referral(self, user_id: int):
        """Увеличить счетчик рефералов"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users
            SET referral_count = referral_count + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_referral_count(self, user_id: int) -> int:
        """Получить количество рефералов"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT referral_count FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
