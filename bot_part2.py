# Продолжение bot.py - вспомогательные функции

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
        "• **Варианты действий** (от мягких к жёстким)\n"
        "• **Карта возможных ходов**\n\n"
        "Хочешь апгрейд?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def process_extended_analysis(query, user_id):
    """Обработка расширенного анализа (99₽)"""
    await query.message.reply_text("⏳ **Генерирую расширенный разбор...**\n\nЭто займет 1-2 минуты.", parse_mode='Markdown')
    
    # Создание платежа
    analysis_id = get_user_data(user_id, 'analysis_id')
    db.create_payment(user_id, analysis_id, 50, 'extended')  # доплата 50₽
    
    # Генерация промпта
    prompt = get_extended_prompt(
        situation=get_user_data(user_id, 'situation'),
        participants=get_user_data(user_id, 'participants'),
        agreement_type=get_user_data(user_id, 'agreement_type'),
        agreement_details=get_user_data(user_id, 'agreement_details'),
        completion_criteria=get_user_data(user_id, 'completion_criteria'),
        what_happened=get_user_data(user_id, 'what_happened'),
        evidence=get_user_data(user_id, 'evidence'),
        main_concern=get_user_data(user_id, 'main_concern'),
        refinement_text=get_user_data(user_id, 'refinement_text'),
        user_name=get_user_data(user_id, 'user_name'),
        user_age=get_user_data(user_id, 'user_age'),
        user_gender=get_user_data(user_id, 'user_gender')
    )
    
    # Получение анализа
    try:
        analysis = await gigachat.get_analysis(prompt, tariff="extended")
        
        # Сохранение
        db.update_analysis(analysis_id, final_analysis=analysis, tariff='extended')
        
        await query.message.reply_text(f"✅ **Расширенный анализ готов!**\n\n{analysis}", parse_mode='Markdown')
        
        # Предложение персонализации
        set_user_state(user_id, ConversationState.OFFERING_PERSONALIZATION)
        await offer_personalization(query.message, user_id)
        
    except Exception as e:
        logger.error(f"Error getting extended analysis: {e}")
        await query.message.reply_text(
            "⚠️ **Ошибка при генерации расширенного анализа.**\n\n"
            f"Попробуй ещё раз или обратись к @{ADMIN_USERNAME}",
            parse_mode='Markdown'
        )


async def offer_personalization(message, user_id):
    """Предложение добавить персонализацию"""
    # Проверка - если уже есть персонализация, пропустить
    if get_user_data(user_id, 'user_name'):
        await finalize_analysis(message, user_id)
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, добавить", callback_data="add_personalization")],
        [InlineKeyboardButton("Не нужно", callback_data="skip_personalization")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "📝 **Персонализировать протокол?**\n\n"
        "Ты можешь указать своё имя, возраст и пол,\n"
        "чтобы протокол выглядел более естественно.\n\n"
        "_Это опционально и бесплатно._",
        reply_markup=reply_markup,
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
    
    # Обработка пола
    elif query.data.startswith('gender_'):
        gender_map = {
            'gender_male': 'Мужской',
            'gender_female': 'Женский',
            'gender_skip': None
        }
        
        gender = gender_map.get(query.data)
        if gender:
            set_user_data(user_id, 'user_gender', gender)
        
        # Сохранение персонализации в БД
        analysis_id = get_user_data(user_id, 'analysis_id')
        db.update_analysis(
            analysis_id,
            user_name=get_user_data(user_id, 'user_name'),
            user_age=get_user_data(user_id, 'user_age'),
            user_gender=get_user_data(user_id, 'user_gender')
        )
        
        await finalize_analysis(query.message, user_id)


def main():
    """Запуск бота"""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_TOKEN not found in environment variables")
    
    application = Application.builder().token(token).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_agreement_handler, pattern="^(agreement_|gender_)"))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Bot started with GigaChat API v2.1")
    application.run_polling()


if __name__ == "__main__":
    main()
