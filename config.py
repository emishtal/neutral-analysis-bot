"""
Конфигурация бота
Загрузка переменных окружения
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (для локальной разработки)
load_dotenv()


class Config:
    """Конфигурация приложения"""
    
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # Claude API
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')  # Sonnet 4.5 по умолчанию
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')
    
    # Payment (ЮKassa) - будет позже
    YUKASSA_SHOP_ID = os.getenv('YUKASSA_SHOP_ID')
    YUKASSA_SECRET_KEY = os.getenv('YUKASSA_SECRET_KEY')
    
    # Admin
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'your_support')
    
    @classmethod
    def validate(cls):
        """Проверка обязательных переменных"""
        required = [
            ('TELEGRAM_TOKEN', cls.TELEGRAM_TOKEN),
            ('CLAUDE_API_KEY', cls.CLAUDE_API_KEY),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


# Проверяем конфигурацию при импорте
Config.validate()
