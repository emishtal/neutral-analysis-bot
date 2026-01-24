# Telegram-бот "Нейтральный разбор ситуации" (GigaChat версия)

Бот для нейтрального анализа конфликтных ситуаций с использованием GigaChat API от Сбера.

## 🎯 Возможности

- Протокол из 7 вопросов для сбора информации
- Нейтральный анализ ситуации через GigaChat API
- Два тарифа:
  - 99₽ - Разбор для себя (анализ без советов)
  - 149₽ - Протокол + шаги (анализ + варианты действий)
- Интеграция с Trust Profile
- SQLite база данных

## 📋 Требования

- Python 3.10+
- Telegram Bot Token
- GigaChat API Credentials (Client ID + Client Secret)
- Хостинг: Timeweb Cloud / Selectel / Yandex Cloud

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/emishtal/neutral-analysis-bot.git
cd neutral-analysis-bot
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Настроить переменные окружения

Создай файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполни своими данными:

```env
TELEGRAM_TOKEN=8379809265:AAH-sr*****
GIGACHAT_CLIENT_ID=ваш_client_id
GIGACHAT_CLIENT_SECRET=ваш_client_secret
GIGACHAT_SCOPE=GIGACHAT_API_PERS
```

### 4. Запустить локально

```bash
python bot.py
```

## 🌐 Деплой на Timeweb Cloud

### Автоматический деплой

1. Зарегистрируйся на [Timeweb Cloud](https://timeweb.cloud)
2. Создай VPS (тариф S - 150₽/мес)
3. Настрой автодеплой из GitHub
4. Бот запустится автоматически

**Подробная инструкция:** см. `TIMEWEB_DEPLOY.md`

## 📁 Структура проекта

```
neutral-analysis-bot/
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация
├── database.py         # Работа с БД
├── gigachat_api.py     # GigaChat API интеграция
├── states.py           # State machine
├── prompts.py          # Промпты для GigaChat (2 режима)
├── requirements.txt    # Зависимости
├── .env.example        # Пример переменных
└── README.md           # Эта инструкция
```

## 🔧 Настройка

### Получить Telegram Bot Token

1. Найди [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`
3. Следуй инструкциям
4. Скопируй полученный токен

### Получить GigaChat API Credentials

**Подробная инструкция:** см. `GIGACHAT_SETUP.md`

Коротко:
1. Зайди на [developers.sber.ru](https://developers.sber.ru/portal/products/gigachat-api)
2. Зарегистрируйся
3. Создай приложение
4. Получи Client ID и Client Secret
5. Используй scope: `GIGACHAT_API_PERS`

### Оплата GigaChat API

**GigaChat Lite (бесплатно):**
- 300 запросов/день
- Для MVP - достаточно!

**GigaChat Plus (~3₽ за разбор):**
- Input: 1.2₽ за 1,000 токенов
- Output: 2.4₽ за 1,000 токенов
- Подключается российской картой

**Стоимость при 100 разборах/день:**
- Выручка: 9,900₽/день (99₽ × 100)
- Расходы GigaChat: 350₽/день
- Хостинг: 150₽/мес
- **Прибыль: ~286,000₽/мес**

## 💾 База данных

Бот использует SQLite (файл `database.db`).

**Таблицы:**
- `users` - пользователи бота
- `analysis_requests` - запросы на анализ
- `analysis_results` - результаты анализа

База создается автоматически при первом запуске.

## 🛠️ Разработка

### Локальное тестирование

```bash
# Установи виртуальное окружение
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установи зависимости
pip install -r requirements.txt

# Запусти бота
python bot.py
```

### Просмотр логов

Логи выводятся в консоль. Уровень логирования: INFO.

## 📊 Мониторинг

На Timeweb Cloud логи доступны в панели управления VPS.

## 🔄 Обновление

```bash
git pull origin main
# На Timeweb деплой произойдет автоматически (если настроен)
```

## ⚠️ Важные особенности

### GigaChat API

- OAuth авторизация (токен обновляется автоматически)
- Токен живет 30 минут
- Verify SSL = False (особенность GigaChat API)

### Два режима промпта

**99₽ - Разбор для себя:**
- Фиксация фактов vs интерпретаций
- Указание узких мест
- БЕЗ советов и шагов

**149₽ - Протокол + шаги:**
- Всё из базового
- ПЛЮС нейтральный протокол для передачи
- ПЛЮС варианты действий (не советы!)

## 🐛 Troubleshooting

### Ошибка GigaChat авторизации

```
Error: Failed to get GigaChat access token
```

**Решение:** 
- Проверь `GIGACHAT_CLIENT_ID` и `GIGACHAT_CLIENT_SECRET`
- Убедись что scope = `GIGACHAT_API_PERS`

### Бот не отвечает

**Решение:**
1. Проверь логи
2. Убедись что бот запущен
3. Проверь переменные окружения

### База данных не создается

**Решение:** Убедись что есть права на запись в папку

## 📞 Поддержка

По вопросам: [@your_support](https://t.me/your_support)

## 📝 TODO

- [ ] Интеграция с ЮKassa (реальная оплата)
- [ ] Реферальная система
- [ ] Интеграция с Trust Profile
- [ ] Статистика и аналитика
- [ ] Админ-панель

## 📄 Философия проекта

Подробнее о концепции и границах проекта см. в файлах:
- `_БАЗА_ЗНАНИЙ_О_ПРОЕКТЕ`
- `MVP_GUARDRAILS`

**Ключевые принципы:**
- Факты, а не мнения
- Инфраструктура, а не платформа
- Не решать за людей
- Минимализм везде

## 📄 Лицензия

MIT
