"""
Конфигурация бота
Загрузка переменных окружения для GigaChat API
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (для локальной разработки)
load_dotenv()


class Config:
    """Конфигурация приложения"""
    
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # GigaChat API
    GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID')
    GIGACHAT_CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET')
    GIGACHAT_SCOPE = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')
    
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
            ('GIGACHAT_CLIENT_ID', cls.GIGACHAT_CLIENT_ID),
            ('GIGACHAT_CLIENT_SECRET', cls.GIGACHAT_CLIENT_SECRET),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


# Проверяем конфигурацию при импорте
Config.validate()
