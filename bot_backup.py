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
from prompts import get_basic_prompt, get_extended_prompt, get_extended_audit_prompt

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
    
    # ОБНОВЛЁННЫЙ ТЕКСТ v2.6
    welcome_text = f"""Привет, {user.first_name}! 👋

**Этот бот помогает понять, ГДЕ именно стороны по-разному понимали одну и ту же договорённость.**

Он не ищет виноватых и не даёт советов, а показывает структурную причину, из-за которой разговор зашёл в тупик.

⚠️ **Бот подходит, если:**
✅ Между вами было какое-то ожидание или договорённость
✅ Вы спорите о результате, границах или ответственности
✅ Каждая сторона считает себя правой

❌ **Не подходит для ситуаций:**
❌ Где одна сторона имеет полную власть (руководство игнорирует всё)
❌ Где вы хотите узнать "кто прав"
❌ Где договорённости вообще не было

**Как это работает:**

1️⃣ Ты отвечаешь на 8 вопросов о ситуации
2️⃣ Получаешь **структурный разбор** за 49₽
3️⃣ Можешь **бесплатно уточнить факты** (1 раз)
4️⃣ При желании — **расширенный анализ** за 99₽

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
    
    # Вопрос 8: Что беспокоит → СРАЗУ ПРЕДЛОЖИТЬ ТАРИФ
    elif state == ConversationState.ASKING_Q8_CONCERN:
        set_user_data(user_id, 'main_concern', text)
        set_user_state(user_id, ConversationState.CHOOSING_BASIC_TARIFF)
        
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
        
        # СРАЗУ предложить тариф (БЕЗ подтверждения!)
        keyboard = [[InlineKeyboardButton("💳 49₽ - Разбор для себя", callback_data="pay_basic")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ **Отлично! Все вопросы пройдены.**\n\n"
            "💳 **Выбери тариф:**\n\n"
            "🔹 **РАЗБОР ДЛЯ СЕБЯ — 49₽**\n"
            "Ты получишь:\n"
            "• Структурную причину конфликта\n"
            "• Где именно застрял спор\n"
            "• Что не было определено\n\n"
            "⏳ Разбор готовится 1-2 минуты.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Уточнение фактов
    elif state == ConversationState.ASKING_REFINEMENT:
        set_user_data(user_id, 'refinement_text', text)
        
        # Пересборка разбора с уточнёнными фактами
        await regenerate_basic_analysis(update.message, user_id)


async def process_basic_analysis(query, user_id):
    """Обработка базового анализа (49₽)"""
    await query.message.reply_text("⏳ **Генерирую нейтральный разбор...**\n\nЭто займет 1-2 минуты.", parse_mode='Markdown')
    
    # Создание платежа (пока заглушка)
    analysis_id = get_user_data(user_id, 'analysis_id')
    db.create_payment(user_id, analysis_id, 49, 'basic')
    
    # Генерация промпта
    prompt = get_basic_prompt(
        situation=get_user_data(user_id, 'situation'),
        participants=get_user_data(user_id, 'participants'),
        agreement_type=get_user_data(user_id, 'agreement_type'),
        agreement_details=get_user_data(user_id, 'agreement_details'),
        completion_criteria=get_user_data(user_id, 'completion_criteria'),
        what_happened=get_user_data(user_id, 'what_happened'),
        evidence=get_user_data(user_id, 'evidence'),
        main_concern=get_user_data(user_id, 'main_concern')
    )
    
    # Получение анализа от GigaChat
    try:
        analysis = await gigachat.get_analysis(prompt, tariff="basic")
        
        # Сохранение результата
        db.update_analysis(analysis_id, initial_analysis=analysis, tariff='basic')
        set_user_data(user_id, 'initial_analysis', analysis)
        set_user_data(user_id, 'basic_analysis', analysis)  # НОВОЕ: сохраняем для расширенного
        
        # Отправка результата
        await query.message.reply_text(f"✅ **Анализ готов!**\n\n{analysis}", parse_mode='Markdown')
        
        # Предложение уточнить факты
        set_user_state(user_id, ConversationState.OFFERING_REFINEMENT)
        await offer_refinement(query.message, user_id)
        
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        await query.message.reply_text(
            "⚠️ **Ошибка при генерации анализа.**\n\n"
            f"Попробуй ещё раз или обратись к @{ADMIN_USERNAME}",
            parse_mode='Markdown'
        )


async def regenerate_basic_analysis(message, user_id):
    """Пересборка базового анализа с уточнёнными фактами"""
    await message.reply_text("⏳ **Пересобираю разбор с учётом уточнений...**\n\nПодожди 1-2 минуты.", parse_mode='Markdown')
    
    # Обновление флага
    analysis_id = get_user_data(user_id, 'analysis_id')
    refinement = get_user_data(user_id, 'refinement_text')
    db.update_analysis(analysis_id, facts_updated=True, refinement_text=refinement)
    
    # Генерация промпта с уточнениями
    prompt = get_basic_prompt(
        situation=get_user_data(user_id, 'situation'),
        participants=get_user_data(user_id, 'participants'),
        agreement_type=get_user_data(user_id, 'agreement_type'),
        agreement_details=get_user_data(user_id, 'agreement_details'),
        completion_criteria=get_user_data(user_id, 'completion_criteria'),
        what_happened=get_user_data(user_id, 'what_happened'),
        evidence=get_user_data(user_id, 'evidence'),
        main_concern=get_user_data(user_id, 'main_concern'),
        refinement_text=refinement
    )
    
    # Получение обновлённого анализа
    try:
        analysis = await gigachat.get_analysis(prompt, tariff="basic")
        
        # Сохранение
        db.update_analysis(analysis_id, initial_analysis=analysis)
        set_user_data(user_id, 'initial_analysis', analysis)
        set_user_data(user_id, 'basic_analysis', analysis)  # НОВОЕ: обновляем для расширенного
        
        await message.reply_text(f"✅ **Обновлённый анализ готов!**\n\n{analysis}", parse_mode='Markdown')
        
        # Предложение апгрейда
        set_user_state(user_id, ConversationState.OFFERING_UPGRADE)
        await offer_upgrade(message, user_id)
        
    except Exception as e:
        logger.error(f"Error regenerating analysis: {e}")
        await message.reply_text(
            "⚠️ **Ошибка при пересборке анализа.**\n\n"
            f"Попробуй ещё раз или обратись к @{ADMIN_USERNAME}",
            parse_mode='Markdown'
        )


async def offer_refinement(message, user_id):
    """Предложение уточнить факты"""
    keyboard = [
        [InlineKeyboardButton("📝 Уточнить факты", callback_data="refine_facts")],
        [InlineKeyboardButton("➡️ Продолжить", callback_data="skip_refinement")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "💡 **Часто именно после первого прочтения становится видно,**\n"
        "какие детали не были озвучены или были сформулированы неточно.\n\n"
        "Ты можешь **один раз уточнить или добавить факты**\n"
        "и получить более точный разбор.\n\n"
        "_Уточнение — бесплатно._",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def offer_upgrade(message, user_id):
    """Предложение апгрейда до расширенного тарифа"""
    keyboard = [
        [InlineKeyboardButton("💳 99₽ - Протокол + шаги", callback_data="pay_extended")],
        [InlineKeyboardButton("Нет, спасибо", callback_data="skip_upgrade")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "🔸 **ПРОТОКОЛ + ШАГИ — 99₽** (+50₽ к базовому)\n\n"
        "Всё из базового тарифа, ПЛЮС:\n"
        "• **Нейтральный текст для передачи** другой стороне\n"
        "• **Структурные точки конфликта**\n"
        "• **Карта что не было определено**\n\n"
        "Хочешь апгрейд?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def process_extended_analysis(query, user_id):
    """Обработка расширенного анализа (99₽) с аудитом v3.0"""
    await query.message.reply_text("⏳ **Генерирую расширенный разбор...**\n\nЭто займет 1-2 минуты.", parse_mode='Markdown')
    
    # Создание платежа
    analysis_id = get_user_data(user_id, 'analysis_id')
    db.create_payment(user_id, analysis_id, 50, 'extended')  # доплата 50₽
    
    # Получаем базовый анализ
    basic_analysis = get_user_data(user_id, 'basic_analysis')
    
    # ШАГ 1: Генерация расширенного (v2.8)
    extended_prompt = get_extended_prompt(
        situation=get_user_data(user_id, 'situation'),
        participants=get_user_data(user_id, 'participants'),
        agreement_type=get_user_data(user_id, 'agreement_type'),
        agreement_details=get_user_data(user_id, 'agreement_details'),
        completion_criteria=get_user_data(user_id, 'completion_criteria'),
        what_happened=get_user_data(user_id, 'what_happened'),
        evidence=get_user_data(user_id, 'evidence'),
        main_concern=get_user_data(user_id, 'main_concern'),
        refinement_text=get_user_data(user_id, 'refinement_text'),
        basic_analysis=basic_analysis  # НОВОЕ!
    )
    
    try:
        # Генерация черновика расширенного
        extended_draft = await gigachat.get_analysis(extended_prompt, tariff="extended")
        
        # ШАГ 2: Аудит расширенного (v3.0) - НОВОЕ!
        await query.message.reply_text("⏳ **Проверяю и улучшаю анализ...**", parse_mode='Markdown')
        
        audit_prompt = get_extended_audit_prompt(extended_draft)
        
        # Аудит черновика
        extended_final = await gigachat.get_analysis(audit_prompt, tariff="extended")
        
        # Сохранение
        db.update_analysis(analysis_id, final_analysis=extended_final, tariff='extended')
        
        await query.message.reply_text(f"✅ **Расширенный анализ готов!**\n\n{extended_final}", parse_mode='Markdown')
        
        # Завершение
        await finalize_analysis(query.message, user_id)
        
    except Exception as e:
        logger.error(f"Error getting extended analysis: {e}")
        await query.message.reply_text(
            "⚠️ **Ошибка при генерации расширенного анализа.**\n\n"
            f"Попробуй ещё раз или обратись к @{ADMIN_USERNAME}",
            parse_mode='Markdown'
        )


async def finalize_analysis(message, user_id):
    """Завершение анализа"""
    set_user_state(user_id, ConversationState.COMPLETED)
    
    stats = db.get_user_stats(user_id)
    
    await message.reply_text(
        f"🎉 **Готово!**\n\n"
        f"Ты прошёл **{stats['total_analyses']}** разбор(ов).\n\n"
        f"Если возникнут вопросы — пиши @{ADMIN_USERNAME}\n\n"
        f"Чтобы начать новый разбор, нажми /start",
        parse_mode='Markdown'
    )


# Обработчики для кнопок с типом договорённости
async def button_agreement_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора типа договорённости"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    agreement_types = {
        'agreement_oral': 'Устная',
        'agreement_written': 'Письменная',
        'agreement_partial': 'Частично (что-то обсуждали)',
        'agreement_none': 'Договорённости не было'
    }
    
    if query.data in agreement_types:
        set_user_data(user_id, 'agreement_type', agreement_types[query.data])
        set_user_state(user_id, ConversationState.ASKING_Q4_AGREEMENT_DETAILS)
        
        await query.message.reply_text(
            "📝 **Вопрос 4/8**\n\n"
            "Что именно было оговорено?\n\n"
            "👉 Если можешь, укажи:\n"
            "• какие действия\n"
            "• в какие сроки\n"
            "• на каких условиях\n\n"
            "_(если условий не было — так и напиши)_",
            parse_mode='Markdown'
        )


def main():
    """Запуск бота"""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_TOKEN not found in environment variables")
    
    application = Application.builder().token(token).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_agreement_handler, pattern="^agreement_"))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Bot started with v2.8 + v3.0 audit")
    application.run_polling()


if __name__ == "__main__":
    main()
