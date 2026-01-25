# 🚀 ИНСТРУКЦИЯ ПО ДЕПЛОЮ БОТА V2.1

## ЧТО ИЗМЕНИЛОСЬ

### Новые функции:
✅ 8 вопросов вместо 7 (добавлен ключевой вопрос про критерий выполнения)
✅ Уточнение фактов (1 раз бесплатно)
✅ Дифференциация тарифов: 49₽ (5 пунктов) и 99₽ (7 пунктов)
✅ Промпт v2.1 с антипримерами
✅ Персонализация (опционально)
✅ Улучшенное описание бота в /start

### Технические изменения:
- database.py - новые поля в БД
- states.py - новые состояния
- prompts.py - полностью переписан
- bot.py - новая логика флоу

---

## ПОДГОТОВКА (НА MAC)

### 1. Скачай файлы с Claude

Все файлы в `/mnt/user-data/outputs/bot_v2/`:
- database.py
- states.py
- prompts.py
- bot.py
- gigachat_api.py
- config.py
- requirements.txt
- .env.example

### 2. Обнови локальный репозиторий

```bash
# На Mac
cd ~/Desktop/neutral-analysis-bot

# Скопируй новые файлы (из папки outputs/bot_v2)
# Замени старые файлы новыми

# Проверь что все файлы на месте
ls -la
```

### 3. Обнови GitHub

```bash
# Добавь все изменения
git add .

# Коммит
git commit -m "Bot v2.1: новый флоу, 8 вопросов, уточнение фактов, промпт с антипримерами"

# Пуш
git push origin main
```

---

## ДЕПЛОЙ НА СЕРВЕР

### 1. Подключись к серверу

```bash
ssh root@89.23.101.136
```

### 2. Останови бота

```bash
systemctl stop neutral-bot
```

### 3. Обнови код

```bash
cd /opt/bots/neutral-analysis-bot
git pull origin main
```

### 4. Обнови зависимости (если нужно)

```bash
source venv/bin/activate
pip install -r requirements.txt --break-system-packages
```

### 5. Проверь .env файл

```bash
cat .env
```

**Должно быть:**
```
TELEGRAM_TOKEN=8379809265:AAH-sr8lFC_dbzYC1d4ddrnlDKAhY7EmxAw
GIGACHAT_CLIENT_ID=019bf18f-...  (твой реальный)
GIGACHAT_CLIENT_SECRET=88cb636a-... (твой реальный)
GIGACHAT_SCOPE=GIGACHAT_API_PERS
DATABASE_PATH=/opt/bots/neutral-analysis-bot/database.db
ADMIN_USERNAME=emishtal
```

Если чего-то не хватает - отредактируй:
```bash
nano .env
```

### 6. Обнови БД (автоматически)

База данных обновится автоматически при первом запуске бота.
Старые данные сохранятся, добавятся только новые поля.

### 7. Запусти бота

```bash
systemctl start neutral-bot
```

### 8. Проверь статус

```bash
systemctl status neutral-bot
```

**Должно показать:**
```
● neutral-bot.service - Neutral Analysis Telegram Bot
   Active: active (running)
```

### 9. Проверь логи

```bash
journalctl -u neutral-bot -n 50
```

**Должно быть:**
```
Bot started with GigaChat API v2.1
Application started
```

**НЕ должно быть ошибок:**
```
Failed to get GigaChat access token
ModuleNotFoundError
```

---

## ТЕСТИРОВАНИЕ

### 1. Тест базового флоу

**В Telegram на телефоне:**

1. Открой @neutral_analysis_bot
2. Отправь `/start`
3. **Проверь:** Есть описание бота? ✅
4. Нажми "🚀 Начать разбор"
5. Пройди все 8 вопросов
6. **Проверь:** Вопрос 5 про "критерий выполнения"? ✅
7. Подтверди данные
8. Нажми "49₽ - Разбор для себя"
9. **Проверь:** Анализ из 5 пунктов? ✅
10. **Проверь:** Есть пункт "Структурная причина конфликта"? ✅

### 2. Тест уточнения фактов

1. После получения базового разбора
2. Нажми "📝 Уточнить факты"
3. Напиши что-то: "Ещё забыл добавить, что..."
4. **Проверь:** Разбор пересобрался с учётом уточнений? ✅
5. **Проверь:** Кнопка "Уточнить факты" больше не появляется? ✅

### 3. Тест апгрейда до 99₽

1. После базового разбора (с уточнением или без)
2. Нажми "99₽ - Протокол + шаги"
3. **Проверь:** Анализ из 7 пунктов? ✅
4. **Проверь:** Есть пункт 6 "Нейтральный протокол"? ✅
5. **Проверь:** Есть пункт 7 "Варианты действий"? ✅
6. **Проверь:** Варианты конкретные, а не общие? ✅

### 4. Тест персонализации (опционально)

1. После расширенного разбора
2. Если появилось предложение персонализации
3. Нажми "✅ Да, добавить"
4. Введи имя, возраст, пол
5. **Проверь:** Протокол обновился с учётом данных? ✅

---

## ЧТО ДЕЛАТЬ ЕСЛИ ЧТО-ТО СЛОМАЛОСЬ

### Ошибка: ModuleNotFoundError

```bash
cd /opt/bots/neutral-analysis-bot
source venv/bin/activate
pip install -r requirements.txt --break-system-packages
systemctl restart neutral-bot
```

### Ошибка: GigaChat авторизация

```bash
# Проверь .env файл
cat .env | grep GIGACHAT

# Должны быть заполнены Client ID и Secret (36 символов каждый)
# Если пусто или xxxxx - исправь
nano .env
```

### Бот не отвечает

```bash
# Проверь статус
systemctl status neutral-bot

# Посмотри логи
journalctl -u neutral-bot -n 100

# Перезапусти
systemctl restart neutral-bot
```

### База данных не обновилась

```bash
# Удали старую БД (ОСТОРОЖНО! Потеряются данные)
cd /opt/bots/neutral-analysis-bot
rm database.db

# Перезапусти бота (создаст новую БД)
systemctl restart neutral-bot
```

---

## ОТКАТ НА СТАРУЮ ВЕРСИЮ

Если что-то критически сломалось:

```bash
cd /opt/bots/neutral-analysis-bot
git log --oneline  # посмотри последние коммиты
git checkout <hash_старого_коммита>
systemctl restart neutral-bot
```

---

## ПОЛЕЗНЫЕ КОМАНДЫ

### Посмотреть логи в реальном времени
```bash
journalctl -u neutral-bot -f
```
(Control+C чтобы выйти)

### Перезапустить бота
```bash
systemctl restart neutral-bot
```

### Остановить бота
```bash
systemctl stop neutral-bot
```

### Запустить бота
```bash
systemctl start neutral-bot
```

### Проверить статус
```bash
systemctl status neutral-bot
```

### Посмотреть .env
```bash
cd /opt/bots/neutral-analysis-bot
cat .env
```

---

## ЧЕКЛИСТ УСПЕШНОГО ДЕПЛОЯ

- [ ] Код обновлён на GitHub
- [ ] Код загружен на сервер (git pull)
- [ ] Бот запущен без ошибок
- [ ] Тест: /start показывает новое описание
- [ ] Тест: 8 вопросов (не 7)
- [ ] Тест: Базовый анализ (49₽) - 5 пунктов
- [ ] Тест: Уточнение фактов работает
- [ ] Тест: Расширенный анализ (99₽) - 7 пунктов
- [ ] Тест: GigaChat отвечает (не ошибка)
- [ ] Логи чистые (нет ошибок авторизации)

---

## КОНТАКТЫ

Если что-то непонятно или не работает:
- Telegram: @emishtal
- Логи бота: `journalctl -u neutral-bot -n 100`

**Удачи с запуском! 🚀**
