import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

from database import Database
from states import (
    ConversationState, get_user_state, set_user_state,
    get_user_data, set_user_data, clear_user_data
)
from gigachat_api import GigaChatAPI
from prompts import get_basic_prompt, get_extended_prompt

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')
db = Database(DATABASE_PATH)
gigachat = GigaChatAPI()

# Константы
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'your_support')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие и описание бота"""
    user = update.effective_user
    db.create_user(user.id, user.username, user.first_name)
    
    # Очистка предыдущей сессии
    clear_user_data(user.id)
    set_user_state(user.id, ConversationState.START)
    
    welcome_text = f"""Привет, {user.first_name}! 👋

**Я помогу разобрать конфликтную ситуацию нейтрально.**

⚠️ **Важно понимать:**
• Я не психолог и не юрист
• Я не решаю, кто прав или виноват  
• Я просто **прояснил структуру** расхождений

**Как это работает:**

1️⃣ Ты отвечаешь на 8 вопросов о ситуации
2️⃣ Получаешь **структурный разбор** за 49₽
3️⃣ Можешь **бесплатно уточнить факты** (1 раз)
4️⃣ При желании — **протокол для передачи** за 99₽

💡 **Польза уже в процессе:**
Даже само описание ситуации по вопросам помогает посмотреть на проблему под другим углом.

**Чем подробнее опишешь — тем точнее результат!**

Готов начать?"""
    
    keyboard = [[InlineKeyboardButton("🚀 Начать разбор", callback_data="start_analysis")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Начало разбора
    if query.data == "start_analysis":
        set_user_state(user_id, ConversationState.ASKING_Q1_SITUATION)
        set_user_data(user_id, 'analysis_id', db.create_analysis(user_id))
        
        await query.message.reply_text(
            "📝 **Вопрос 1/8**\n\n"
            "Опиши ситуацию кратко, без оценок.\n"
            "2–3 предложения.\n\n"
            "👉 **Что произошло фактически?**\n\n"
            "_Не пиши, кто плохой. Пиши, что случилось._",
            parse_mode='Markdown'
        )
    
    # Подтверждение данных
    elif query.data == "confirm_data_yes":
        set_user_state(user_id, ConversationState.CHOOSING_BASIC_TARIFF)
        
        keyboard = [[InlineKeyboardButton("💳 49₽ - Разбор для себя", callback_data="pay_basic")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "💳 **Выбери тариф:**\n\n"
            "🔹 **РАЗБОР ДЛЯ СЕБЯ — 49₽**\n"
            "Ты выйдешь с ясной картиной:\n"
            "• Что произошло (факты vs эмоции)\n"
            "• Где именно застрял конфликт\n"
            "• Что не хватает для понимания\n\n"
            "⏳ После оплаты разбор готовится 1-2 минуты.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "confirm_data_no":
        set_user_state(user_id, ConversationState.ASKING_Q1_SITUATION)
        await query.message.reply_text(
            "Хорошо, давай пройдём вопросы заново.\n\n"
            "📝 **Вопрос 1/8**\n\n"
            "Опиши ситуацию кратко, без оценок.\n"
            "2–3 предложения.\n\n"
            "👉 **Что произошло фактически?**",
            parse_mode='Markdown'
        )
    
    # Оплата базового тарифа (49₽)
    elif query.data == "pay_basic":
        await process_basic_analysis(query, user_id)
    
    # Уточнение фактов
    elif query.data == "refine_facts":
        set_user_state(user_id, ConversationState.ASKING_REFINEMENT)
        await query.message.reply_text(
            "💡 **Уточнение фактов**\n\n"
            "Напиши, что хочешь добавить или уточнить:\n"
            "• Дополнительные детали\n"
            "• Исправления\n"
            "• Важные нюансы\n\n"
            "_После этого разбор будет пересобран бесплатно._",
            parse_mode='Markdown'
        )
    
    elif query.data == "skip_refinement":
        set_user_state(user_id, ConversationState.OFFERING_UPGRADE)
        await offer_upgrade(query.message, user_id)
    
    # Оплата расширенного тарифа (99₽)
    elif query.data == "pay_extended":
        await process_extended_analysis(query, user_id)
    
    elif query.data == "skip_upgrade":
        set_user_state(user_id, ConversationState.OFFERING_PERSONALIZATION)
        await offer_personalization(query.message, user_id)
    
    # Персонализация
    elif query.data == "add_personalization":
        set_user_state(user_id, ConversationState.ASKING_NAME)
        await query.message.reply_text(
            "📝 **Персонализация разбора**\n\n"
            "Как тебя зовут?\n"
            "_(Или напиши «пропустить»)_",
            parse_mode='Markdown'
        )
    
    elif query.data == "skip_personalization":
        await finalize_analysis(query.message, user_id)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    text = update.message.text
    
    # Вопрос 1: Описание ситуации
    if state == ConversationState.ASKING_Q1_SITUATION:
        set_user_data(user_id, 'situation', text)
        set_user_state(user_id, ConversationState.ASKING_Q2_PARTICIPANTS)
        
        await update.message.reply_text(
            "📝 **Вопрос 2/8**\n\n"
            "Кто участвует в ситуации?\n\n"
            "👉 Перечисли всех, кто:\n"
            "• напрямую вовлечён\n"
            "• или влияет на происходящее\n\n"
            "_(например: я и сын, я и заказчик, я, партнёр и бухгалтер)_",
            parse_mode='Markdown'
        )
    
    # Вопрос 2: Участники
    elif state == ConversationState.ASKING_Q2_PARTICIPANTS:
        set_user_data(user_id, 'participants', text)
        set_user_state(user_id, ConversationState.ASKING_Q3_AGREEMENT)
        
        keyboard = [
            [InlineKeyboardButton("Устная", callback_data="agreement_oral")],
            [InlineKeyboardButton("Письменная", callback_data="agreement_written")],
            [InlineKeyboardButton("Частично (что-то обсуждали)", callback_data="agreement_partial")],
            [InlineKeyboardButton("Договорённости не было", callback_data="agreement_none")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📝 **Вопрос 3/8**\n\n"
            "Была ли между вами договорённость?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Вопрос 4: Детали договорённости
    elif state == ConversationState.ASKING_Q4_AGREEMENT_DETAILS:
        set_user_data(user_id, 'agreement_details', text)
        set_user_state(user_id, ConversationState.ASKING_Q5_COMPLETION)
        
        await update.message.reply_text(
            "📝 **Вопрос 5/8** ⚠️ **КЛЮЧЕВОЙ ВОПРОС!**\n\n"
            "Как ты понимаешь, что задача считается **выполненной**?\n\n"
            "👉 Опиши:\n"
            "• достаточно ли просто сделать действие\n"
            "• или важен результат / качество\n\n"
            "_(например: «просто помыть посуду» или «чтобы кухня была чистой»)_",
            parse_mode='Markdown'
        )
    
    # Вопрос 5: Критерий выполнения (КЛЮЧЕВОЙ!)
    elif state == ConversationState.ASKING_Q5_COMPLETION:
        set_user_data(user_id, 'completion_criteria', text)
        set_user_state(user_id, ConversationState.ASKING_Q6_WHAT_HAPPENED)
        
        await update.message.reply_text(
            "📝 **Вопрос 6/8**\n\n"
            "Что произошло фактически?\n\n"
            "👉 Что было сделано, а что — нет\n"
            "👉 Если есть спорные моменты — опиши их",
            parse_mode='Markdown'
        )
    
    # Вопрос 6: Что произошло
    elif state == ConversationState.ASKING_Q6_WHAT_HAPPENED:
        set_user_data(user_id, 'what_happened', text)
        set_user_state(user_id, ConversationState.ASKING_Q7_EVIDENCE)
        
        await update.message.reply_text(
            "📝 **Вопрос 7/8**\n\n"
            "Есть ли что-то, что подтверждает происходящее?\n"
            "• переписка\n"
            "• скриншоты\n"
            "• свидетели\n"
            "• ничего нет\n\n"
            "_(достаточно описать словами)_",
            parse_mode='Markdown'
        )
    
    # Вопрос 7: Доказательства
    elif state == ConversationState.ASKING_Q7_EVIDENCE:
        set_user_data(user_id, 'evidence', text)
        set_user_state(user_id, ConversationState.ASKING_Q8_CONCERN)
        
        await update.message.reply_text(
            "📝 **Вопрос 8/8** _(последний!)_\n\n"
            "Что тебя больше всего беспокоит в этой ситуации?\n\n"
            "👉 Не обвиняй.\n"
            "👉 Напиши, что именно для тебя критично.\n\n"
            "_(например: сроки, доверие, повторяемость, последствия)_",
            parse_mode='Markdown'
        )
    
    # Вопрос 8: Что беспокоит
    elif state == ConversationState.ASKING_Q8_CONCERN:
        set_user_data(user_id, 'main_concern', text)
        set_user_state(user_id, ConversationState.CONFIRMING_DATA)
        
        # Сохранение в БД
        analysis_id = get_user_data(user_id, 'analysis_id')
        db.update_analysis(
            analysis_id,
            situation=get_user_data(user_id, 'situation'),
            participants=get_user_data(user_id, 'participants'),
            agreement_type=get_user_data(user_id, 'agreement_type'),
            agreement_details=get_user_data(user_id, 'agreement_details'),
            completion_criteria=get_user_data(user_id, 'completion_criteria'),
            what_happened=get_user_data(user_id, 'what_happened'),
            evidence=get_user_data(user_id, 'evidence'),
            main_concern=text
        )
        
        # Показать сводку
        summary = f"""📋 **Итоговая сводка:**

**Ситуация:** {get_user_data(user_id, 'situation')[:100]}...
**Участники:** {get_user_data(user_id, 'participants')}
**Договорённость:** {get_user_data(user_id, 'agreement_type')}

Всё верно?"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Да, всё верно", callback_data="confirm_data_yes")],
            [InlineKeyboardButton("✏️ Исправить", callback_data="confirm_data_no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(summary, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Уточнение фактов
    elif state == ConversationState.ASKING_REFINEMENT:
        set_user_data(user_id, 'refinement_text', text)
        
        # Пересборка разбора с уточнёнными фактами
        await regenerate_basic_analysis(update.message, user_id)
    
    # Ввод имени
    elif state == ConversationState.ASKING_NAME:
        if text.lower() != 'пропустить':
            set_user_data(user_id, 'user_name', text)
        
        set_user_state(user_id, ConversationState.ASKING_AGE)
        await update.message.reply_text(
            "Сколько тебе лет?\n"
            "_(Или напиши «пропустить»)_"
        )
    
    # Ввод возраста
    elif state == ConversationState.ASKING_AGE:
        if text.lower() != 'пропустить':
            try:
                age = int(text)
                set_user_data(user_id, 'user_age', age)
            except ValueError:
                pass
        
        set_user_state(user_id, ConversationState.ASKING_GENDER)
        
        keyboard = [
            [InlineKeyboardButton("Мужской", callback_data="gender_male")],
            [InlineKeyboardButton("Женский", callback_data="gender_female")],
            [InlineKeyboardButton("Не важно", callback_data="gender_skip")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Твой пол?",
            reply_markup=reply_markup
        )


# Продолжение следует в части 2...
