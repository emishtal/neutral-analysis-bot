# Telegram-бот "Нейтральный разбор ситуации"

Бот для нейтрального анализа конфликтных ситуаций с использованием Claude AI.

## 🎯 Возможности

- Протокол из 7 вопросов для сбора информации
- Нейтральный анализ ситуации через Claude API
- Два тарифа: базовый (99₽) и расширенный (149₽)
- Интеграция с Trust Profile
- SQLite база данных

## 📋 Требования

- Python 3.10+
- Telegram Bot Token
- Claude API Key
- Хостинг (Render.com / Railway.app / VPS)

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
CLAUDE_API_KEY=sk-ant-api03-*****
```

### 4. Запустить локально

```bash
python bot.py
```

## 🌐 Деплой на Render.com

### Автоматический деплой

1. Зарегистрируйся на [Render.com](https://render.com) через GitHub
2. Создай новый **Web Service**
3. Подключи свой GitHub репозиторий
4. Render автоматически определит настройки из `render.yaml`
5. Добавь переменные окружения в настройках:
   - `TELEGRAM_TOKEN`
   - `CLAUDE_API_KEY`
6. Нажми "Create Web Service"

### Ручная настройка

Если автоматика не сработала:

- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`

## 📁 Структура проекта

```
neutral-analysis-bot/
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация
├── database.py         # Работа с БД
├── claude_api.py       # Claude API интеграция
├── states.py           # State machine
├── prompts.py          # Промпты для Claude
├── requirements.txt    # Зависимости
├── render.yaml         # Конфиг для Render
├── .env.example        # Пример переменных
└── README.md           # Эта инструкция
```

## 🔧 Настройка

### Получить Telegram Bot Token

1. Найди [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`
3. Следуй инструкциям
4. Скопируй полученный токен

### Получить Claude API Key

1. Зайди на [console.anthropic.com](https://console.anthropic.com)
2. Зарегистрируйся (Individual account)
3. Перейди в раздел "API Keys"
4. Создай новый ключ
5. Скопируй ключ (показывается только один раз!)

### Привязать карту к Claude API

⚠️ **Важно**: Claude API требует оплату картой (не РФ)

**Рабочие варианты:**
- Карта из Киргизии, Казахстана, и др. СНГ
- Виртуальная карта (Wise, Revolut)
- Карта друга/знакомого за границей

**Минимальный депозит**: $5

**Примерная стоимость**: 
- 1 разбор = ~$0.015 (1.5₽)
- 100 разборов = ~$1.50 (150₽)

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

На Render.com логи доступны в реальном времени:
- Dashboard → Твой сервис → Logs

## 🔄 Обновление

```bash
git pull origin main
# На Render деплой произойдет автоматически
```

## ⚠️ Известные ограничения

1. **Render.com бесплатный tier:**
   - Засыпает после 15 минут неактивности
   - Просыпается ~30-50 секунд
   - Для продакшена лучше Railway.app или VPS

2. **Claude API:**
   - Требует карту не из РФ
   - Rate limits: 50 запросов/минуту

3. **Платежи (ЮKassa):**
   - Пока не реализовано
   - Запланировано в Phase 2

## 🐛 Troubleshooting

### Бот не отвечает

1. Проверь логи на Render
2. Убедись что сервис запущен
3. Проверь переменные окружения

### Ошибка Claude API

```
Error: неверный API ключ
```

**Решение**: Проверь `CLAUDE_API_KEY` в настройках

### База данных не создается

**Решение**: Убедись что есть права на запись в папку

## 📞 Поддержка

По вопросам: [@your_support](https://t.me/your_support)

## 📝 TODO

- [ ] Интеграция с ЮKassa
- [ ] Реферальная система
- [ ] Интеграция с Trust Profile
- [ ] Статистика и аналитика
- [ ] Админ-панель

## 📄 Лицензия

MIT
