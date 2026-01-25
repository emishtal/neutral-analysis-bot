import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# GigaChat API
GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID')
GIGACHAT_CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET')
GIGACHAT_SCOPE = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

# Admin
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'your_support')
