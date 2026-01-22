"""
Telegram-бот "Нейтральный разбор ситуации"
Основной файл с логикой бота и обработчиками
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from config import Config
from database import Database
from claude_api import ClaudeAPI
from states import States
from prompts import get_analysis_prompt

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
db = Database()
claude = ClaudeAPI()


# ============================================================
# КОМАНДЫ И СТАРТ
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Команда /start - начало работы"""
    user = update.effective_user
    
    # Сохраняем пользователя в БД
    db.create_user(user.id, user.username, user.first_name)
    
    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я помогу разобрать конфликтную ситуацию нейтрально.\n\n"
        "⚠️ Важно понимать:\n"
        "• Я не психолог и не юрист\n"
        "• Я не решаю, кто прав или виноват\n"
        "• Я просто фиксирую факты и показываю разные точки зрения\n\n"
        "Готов начать?"
    )
    
    keyboard = [["Да, начнем"], ["Что это такое?"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return States.INTRO


async def intro_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ответа на приветствие"""
    text = update.message.text
    
    if "Что это такое" in text:
        explanation = (
            "📋 Как это работает:\n\n"
            "1. Я задам тебе несколько вопросов о ситуации\n"
            "2. Ты ответишь своими словами\n"
            "3. После всех вопросов - оплата (99₽ или 149₽)\n"
            "4. Я проанализирую ситуацию нейтрально\n"
            "5. Ты получишь структурированный разбор\n\n"
            "Весь процесс займет 5-10 минут.\n\n"
            "Начнем?"
        )
        keyboard = [["Да, начнем"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(explanation, reply_markup=reply_markup)
        return States.INTRO
    
    # Переход к контексту
    await update.message.reply_text(
        "Отлично! Начинаем.\n\n"
        "📝 Вопрос 1/7\n\n"
        "Опиши ситуацию кратко (2-3 предложения).\n"
        "Что произошло?",
        reply_markup=ReplyKeyboardRemove()
    )
    return States.CONTEXT


# ============================================================
# ПРОТОКОЛ ВОПРОСОВ
# ============================================================

async def context_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вопрос 1: Контекст ситуации"""
    context.user_data['context'] = update.message.text
    
    await update.message.reply_text(
        "📝 Вопрос 2/7\n\n"
        "Кто участники конфликта?\n"
        "(Например: я и клиент, я и коллега, я и друг)"
    )
    return States.PARTICIPANTS


async def participants_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вопрос 2: Участники"""
    context.user_data['participants'] = update.message.text
    
    await update.message.reply_text(
        "📝 Вопрос 3/7\n\n"
        "Была ли между вами договоренность?\n"
        "(Например: устная договоренность, письменный контракт, или ничего формального)"
    )
    return States.AGREEMENT_TYPE


async def agreement_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вопрос 3: Тип договоренности"""
    context.user_data['agreement_type'] = update.message.text
    
    await update.message.reply_text(
        "📝 Вопрос 4/7\n\n"
        "Что именно было оговорено?\n"
        "(Сроки, условия, оплата - всё что помнишь)"
    )
    return States.AGREEMENT_TEXT


async def agreement_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вопрос 4: Суть договоренности"""
    context.user_data['agreement_text'] = update.message.text
    
    await update.message.reply_text(
        "📝 Вопрос 5/7\n\n"
        "Что произошло фактически?\n"
        "(Что было сделано или НЕ сделано)"
    )
    return States.FACTS


async def facts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вопрос 5: Факты"""
    context.user_data['facts'] = update.message.text
    
    await update.message.reply_text(
        "📝 Вопрос 6/7\n\n"
        "Есть ли доказательства?\n"
        "(Переписка, скриншоты, свидетели, документы - опиши что есть)"
    )
    return States.EVIDENCE


async def evidence_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вопрос 6: Доказательства"""
    context.user_data['evidence'] = update.message.text
    
    await update.message.reply_text(
        "📝 Вопрос 7/7 (последний)\n\n"
        "Что тебя больше всего беспокоит в этой ситуации?"
    )
    return States.CONCERN


async def concern_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вопрос 7: Что беспокоит"""
    context.user_data['concern'] = update.message.text
    
    # Формируем итоговую сводку
    summary = (
        "📋 Итоговая сводка:\n\n"
        f"Ситуация: {context.user_data['context'][:100]}...\n"
        f"Участники: {context.user_data['participants']}\n"
        f"Договоренность: {context.user_data['agreement_type']}\n\n"
        "Всё верно?"
    )
    
    keyboard = [["Да, всё верно"], ["Начать заново"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(summary, reply_markup=reply_markup)
    return States.SUMMARY


async def summary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждение сводки"""
    text = update.message.text
    
    if "заново" in text.lower():
        await update.message.reply_text(
            "Хорошо, начнем сначала.\n\n"
            "📝 Вопрос 1/7\n\n"
            "Опиши ситуацию кратко (2-3 предложения).",
            reply_markup=ReplyKeyboardRemove()
        )
        return States.CONTEXT
    
    # Переход к оплате
    payment_text = (
        "💳 Выбери тариф:\n\n"
        "🔹 Базовый разбор - 99₽\n"
        "• Структурированный анализ\n"
        "• Фиксация фактов\n"
        "• Возможные варианты действий\n\n"
        "🔸 Расширенный разбор - 149₽\n"
        "• Всё из базового\n"
        "• Более детальный анализ\n"
        "• Больше вариантов действий\n"
        "• Анализ рисков\n\n"
        "⏳ После оплаты разбор готовится 1-2 минуты."
    )
    
    keyboard = [["99₽ - Базовый"], ["149₽ - Расширенный"], ["Отменить"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(payment_text, reply_markup=reply_markup)
    return States.PAYMENT


async def payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора тарифа (пока без реальной оплаты)"""
    text = update.message.text
    
    if "Отменить" in text:
        await update.message.reply_text(
            "Анализ отменен. Используй /start чтобы начать заново.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Определяем тариф
    if "99" in text:
        tariff = "basic"
        price = 99
    else:
        tariff = "extended"
        price = 149
    
    context.user_data['tariff'] = tariff
    context.user_data['price'] = price
    
    # TODO: Здесь будет интеграция с ЮKassa
    # Пока делаем mock оплаты
    
    await update.message.reply_text(
        "⏳ Генерирую нейтральный разбор...\n\n"
        "Это займет 1-2 минуты.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Сохраняем запрос в БД
    user_id = update.effective_user.id
    request_id = db.create_analysis_request(
        user_id=user_id,
        context=context.user_data['context'],
        participants=context.user_data['participants'],
        agreement_type=context.user_data['agreement_type'],
        agreement_text=context.user_data['agreement_text'],
        facts=context.user_data['facts'],
        evidence=context.user_data['evidence'],
        concern=context.user_data['concern'],
        tariff=tariff,
        price=price
    )
    
    # Формируем промпт для Claude
    prompt = get_analysis_prompt(context.user_data, tariff)
    
    # Отправляем запрос в Claude
    try:
        analysis = await claude.get_analysis(prompt)
        
        # Сохраняем результат
        db.save_analysis_result(request_id, analysis)
        
        # Отправляем результат пользователю
        await update.message.reply_text(
            "✅ Анализ готов!\n\n" + analysis
        )
        
        # Предложение Trust Profile
        trust_profile_text = (
            "\n\n━━━━━━━━━━━━━━━━━\n\n"
            "💡 Хочешь, чтобы таких ситуаций было меньше?\n\n"
            "Попробуй Trust Profile - фиксируй факты о выполненных работах, "
            "чтобы не было споров в будущем.\n\n"
            "Узнать больше: /trustprofile"
        )
        await update.message.reply_text(trust_profile_text)
        
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при анализе.\n"
            "Попробуй позже или напиши в поддержку: @your_support"
        )
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена разговора"""
    await update.message.reply_text(
        "Разбор отменен. Используй /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ============================================================
# ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ
# ============================================================

async def trustprofile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о Trust Profile"""
    text = (
        "🛡️ Trust Profile\n\n"
        "Платформа для фиксации фактов о выполненных работах.\n\n"
        "Как это помогает:\n"
        "• Фиксируешь договоренности с клиентом\n"
        "• Клиент подтверждает выполнение\n"
        "• У тебя есть подтвержденная история\n"
        "• Меньше споров в будущем\n\n"
        "Скоро запустим!\n"
        "Хочешь попасть в ранний доступ? Напиши: /early_access"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    text = (
        "🤖 Доступные команды:\n\n"
        "/start - Начать новый разбор\n"
        "/cancel - Отменить текущий разбор\n"
        "/trustprofile - Узнать о Trust Profile\n"
        "/help - Эта справка\n\n"
        "По вопросам: @your_support"
    )
    await update.message.reply_text(text)


# ============================================================
# MAIN - ЗАПУСК БОТА
# ============================================================

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Conversation Handler для основного флоу
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.INTRO: [MessageHandler(filters.TEXT & ~filters.COMMAND, intro_handler)],
            States.CONTEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, context_handler)],
            States.PARTICIPANTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, participants_handler)],
            States.AGREEMENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, agreement_type_handler)],
            States.AGREEMENT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, agreement_text_handler)],
            States.FACTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, facts_handler)],
            States.EVIDENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, evidence_handler)],
            States.CONCERN: [MessageHandler(filters.TEXT & ~filters.COMMAND, concern_handler)],
            States.SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, summary_handler)],
            States.PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Добавляем handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('trustprofile', trustprofile_command))
    application.add_handler(CommandHandler('help', help_command))
    
    # Запускаем бота
    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
