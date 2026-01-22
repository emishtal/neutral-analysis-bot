# КОМАНДЫ ДЛЯ ЗАГРУЗКИ НА GITHUB

## ШАГ 1: Перейди в папку где хочешь хранить проект

```bash
cd ~/Documents  # или любая другая папка
```

## ШАГ 2: Создай репозиторий на GitHub

1. Зайди на https://github.com/new
2. Repository name: `neutral-analysis-bot`
3. Description: `Telegram-бот для нейтрального разбора конфликтов`
4. Выбери: **Private** (или Public если хочешь открытый код)
5. ❗ НЕ создавай README, .gitignore, license (у нас уже есть)
6. Нажми "Create repository"

## ШАГ 3: Скачай файлы проекта

Я отправлю тебе архив с файлами. Распакуй его в папку `neutral-analysis-bot`.

Или скопируй файлы вручную из того места, где я их создал.

## ШАГ 4: Инициализируй Git и загрузи код

Открой Terminal (Терминал на macOS) и выполни команды по порядку:

```bash
# Перейди в папку проекта
cd ~/Documents/neutral-analysis-bot

# Инициализируй Git
git init

# Добавь все файлы
git add .

# Сделай первый коммит
git commit -m "Initial commit: Telegram bot for neutral conflict analysis"

# Добавь удаленный репозиторий (замени emishtal на свой username если другой)
git remote add origin https://github.com/emishtal/neutral-analysis-bot.git

# Переименуй ветку в main (если нужно)
git branch -M main

# Загрузи код на GitHub
git push -u origin main
```

### Если попросит авторизацию:

GitHub больше не принимает пароль. Нужен Personal Access Token:

1. Зайди на https://github.com/settings/tokens
2. "Generate new token" → "Generate new token (classic)"
3. Название: `neutral-bot-deploy`
4. Выбери срок: 90 days
5. Поставь галочку: `repo` (все остальное не нужно)
6. Создай токен и СКОПИРУЙ его
7. Используй этот токен вместо пароля

## ШАГ 5: Создай файл .env с секретами

❗ ЭТОТ ФАЙЛ НЕ ЗАГРУЖАЕТСЯ НА GITHUB (он в .gitignore)

```bash
# В папке проекта создай файл .env
nano .env
```

Вставь свои данные:

```env
TELEGRAM_TOKEN=8379809265:AAH-sr*****
CLAUDE_API_KEY=sk-ant-api03-*****
CLAUDE_MODEL=claude-sonnet-4-20250514
DATABASE_PATH=database.db
ADMIN_USERNAME=your_support
```

Сохрани: `Ctrl+O` → `Enter` → `Ctrl+X`

## ШАГ 6: Проверь что всё на GitHub

Зайди на https://github.com/emishtal/neutral-analysis-bot

Должны быть все файлы кроме `.env` (он секретный)

---

## ГОТОВО! 🎉

Теперь можно деплоить на Render.com

Следующий шаг: я дам инструкцию по деплою на Render.
