# ИНСТРУКЦИЯ: Деплой бота на Timeweb Cloud

## 🎯 Что получим в итоге

После выполнения инструкции:
- ✅ Бот работает 24/7
- ✅ Автоматический деплой при push в GitHub
- ✅ Логи в реальном времени
- ✅ Стоимость: 150₽/мес

---

## 📋 ШАГ 1: Регистрация на Timeweb Cloud (5 минут)

### 1.1. Зайди на сайт

**URL:** https://timeweb.cloud

### 1.2. Нажми "Регистрация"

**Что потребуется:**
- Email
- ФИО
- Телефон (российский номер)
- Придумай пароль

### 1.3. Подтверди email

Проверь почту, перейди по ссылке.

### 1.4. Пройди верификацию

Может попросить:
- Фото паспорта
- Селфи с паспортом
- Подтверждение телефона

**Это нормально!** Для предотвращения мошенничества.

Верификация занимает от 5 минут до 24 часов.

---

## 📋 ШАГ 2: Привязка карты и пополнение (5 минут)

### 2.1. Зайди в "Баланс"

После входа:
1. Личный кабинет
2. "Баланс" или "Billing"

### 2.2. Привяжи карту

**Принимают:**
- ✅ Карты РФ (Visa, MasterCard, Мир)
- ✅ Карты СНГ (Казахстан, Киргизия и др.)

**Вводишь:**
- Номер карты
- Срок действия
- CVV
- Имя держателя

### 2.3. Пополни баланс

**Минимальная сумма:** 100₽

**Рекомендую:** 300₽ на первый раз
- Хватит на 2 месяца работы VPS
- Или на месяц + запас

**Способы пополнения:**
- Банковская карта
- ЮMoney
- QIWI
- Криптовалюта

---

## 📋 ШАГ 3: Создание VPS (10 минут)

### 3.1. Создай новый сервер

1. Нажми "+ Создать" → "VPS"
2. Или "Серверы" → "+ Добавить VPS"

### 3.2. Выбери конфигурацию

**Операционная система:**
- Выбери: **Ubuntu 22.04 LTS** или **Ubuntu 24.04 LTS**

**Тариф:**

**VPS-S (РЕКОМЕНДУЮ):**
- CPU: 1 vCore
- RAM: 1 GB
- SSD: 10 GB
- **Цена: 150₽/мес**

**VPS-M (если планируешь масштабировать):**
- CPU: 2 vCore
- RAM: 2 GB
- SSD: 20 GB
- **Цена: 300₽/мес**

**Для бота VPS-S достаточно!**

### 3.3. Настройки сервера

**Имя сервера:**
```
neutral-bot
```

**Регион:**
- Москва (быстрее для РФ пользователей)
- Или любой другой

**SSH ключ:**
- Если есть - добавь
- Если нет - пропусти (используем пароль)

**Дополнительные опции:**
- Бэкапы - можно включить позже
- Monitoring - опционально

### 3.4. Создай сервер

Нажми "Создать VPS"

**Время создания:** 1-2 минуты

**После создания получишь:**
- IP адрес сервера
- Root пароль (на email)

---

## 📋 ШАГ 4: Подключение к серверу (5 минут)

### 4.1. Открой Terminal (macOS)

Приложение "Терминал" на Mac

### 4.2. Подключись по SSH

```bash
ssh root@твой_ip_адрес
```

**Пример:**
```bash
ssh root@123.45.67.89
```

### 4.3. Введи пароль

Скопируй пароль из email и вставь в терминал

⚠️ **Пароль не отображается при вводе - это нормально!**

Просто вставь и нажми Enter.

### 4.4. Первое подключение

Если спросит:
```
Are you sure you want to continue connecting (yes/no)?
```

Напиши `yes` и нажми Enter.

**Должно появиться:**
```
Welcome to Ubuntu 24.04 LTS
root@neutral-bot:~#
```

✅ **Ты внутри сервера!**

---

## 📋 ШАГ 5: Установка окружения (10 минут)

### 5.1. Обнови систему

```bash
apt update && apt upgrade -y
```

Подожди 2-3 минуты.

### 5.2. Установи Python и зависимости

```bash
apt install -y python3 python3-pip python3-venv git
```

### 5.3. Проверь версию Python

```bash
python3 --version
```

Должно быть: `Python 3.10` или выше.

---

## 📋 ШАГ 6: Клонирование проекта (5 минут)

### 6.1. Создай директорию для проектов

```bash
mkdir -p /opt/bots
cd /opt/bots
```

### 6.2. Клонируй репозиторий с GitHub

```bash
git clone https://github.com/emishtal/neutral-analysis-bot.git
cd neutral-analysis-bot
```

### 6.3. Создай виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
```

Должно появиться `(venv)` в начале строки.

### 6.4. Установи зависимости

```bash
pip install -r requirements.txt
```

Подожди 1-2 минуты.

---

## 📋 ШАГ 7: Настройка переменных окружения (3 минуты)

### 7.1. Создай файл .env

```bash
nano .env
```

### 7.2. Вставь свои данные

```env
TELEGRAM_TOKEN=8379809265:AAH-sr*****
GIGACHAT_CLIENT_ID=твой_client_id
GIGACHAT_CLIENT_SECRET=твой_client_secret
GIGACHAT_SCOPE=GIGACHAT_API_PERS
DATABASE_PATH=/opt/bots/neutral-analysis-bot/database.db
ADMIN_USERNAME=your_support
```

### 7.3. Сохрани файл

Нажми:
- `Ctrl + O` (сохранить)
- `Enter` (подтвердить)
- `Ctrl + X` (выйти)

---

## 📋 ШАГ 8: Настройка автозапуска (systemd) (10 минут)

### 8.1. Создай systemd сервис

```bash
nano /etc/systemd/system/neutral-bot.service
```

### 8.2. Вставь конфигурацию

```ini
[Unit]
Description=Neutral Analysis Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bots/neutral-analysis-bot
Environment="PATH=/opt/bots/neutral-analysis-bot/venv/bin"
ExecStart=/opt/bots/neutral-analysis-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8.3. Сохрани файл

- `Ctrl + O` → `Enter` → `Ctrl + X`

### 8.4. Перезагрузи systemd

```bash
systemctl daemon-reload
```

### 8.5. Запусти бота

```bash
systemctl start neutral-bot
```

### 8.6. Включи автозапуск

```bash
systemctl enable neutral-bot
```

### 8.7. Проверь статус

```bash
systemctl status neutral-bot
```

**Должно быть:**
```
● neutral-bot.service - Neutral Analysis Telegram Bot
   Active: active (running)
```

✅ **БОТ РАБОТАЕТ!**

---

## 📋 ШАГ 9: Проверка работы (5 минут)

### 9.1. Посмотри логи

```bash
journalctl -u neutral-bot -f
```

**Должно появиться:**
```
Bot started with GigaChat API
Application started
HTTP Request: POST https://api.telegram.org/.../getUpdates
```

Нажми `Ctrl + C` чтобы выйти из логов.

### 9.2. Протестируй бота в Telegram

1. Открой https://t.me/neutral_analysis_bot
2. Напиши `/start`
3. Пройди весь флоу
4. Получи анализ!

**Если всё работает - ГОТОВО!** 🎉

---

## 📋 ШАГ 10: Автоматический деплой из GitHub (опционально)

### 10.1. Создай deploy скрипт

```bash
nano /opt/bots/deploy.sh
```

### 10.2. Вставь скрипт

```bash
#!/bin/bash
cd /opt/bots/neutral-analysis-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart neutral-bot
echo "Deploy completed!"
```

### 10.3. Сделай исполняемым

```bash
chmod +x /opt/bots/deploy.sh
```

### 10.4. Теперь деплой делается одной командой

```bash
/opt/bots/deploy.sh
```

**Обновление:**
1. Пушишь код на GitHub
2. Заходишь на сервер: `ssh root@твой_ip`
3. Запускаешь: `/opt/bots/deploy.sh`
4. Готово!

---

## 🛠️ ПОЛЕЗНЫЕ КОМАНДЫ

### Управление ботом

```bash
# Запустить бота
systemctl start neutral-bot

# Остановить бота
systemctl stop neutral-bot

# Перезапустить бота
systemctl restart neutral-bot

# Статус бота
systemctl status neutral-bot

# Логи (последние 100 строк)
journalctl -u neutral-bot -n 100

# Логи (в реальном времени)
journalctl -u neutral-bot -f
```

### Обновление кода

```bash
cd /opt/bots/neutral-analysis-bot
git pull origin main
systemctl restart neutral-bot
```

### Проверка процессов

```bash
# Проверить что бот запущен
ps aux | grep python

# Использование ресурсов
top
```

---

## ⚠️ TROUBLESHOOTING

### Бот не запускается

**Проверь логи:**
```bash
journalctl -u neutral-bot -n 50
```

**Типичные проблемы:**
- Неверные переменные окружения → проверь `.env`
- Нет прав доступа → `chmod +x bot.py`
- Порт занят → перезагрузи сервер

### Ошибка "Permission denied"

```bash
chmod -R 755 /opt/bots/neutral-analysis-bot
```

### База данных не создается

```bash
# Создай вручную
touch /opt/bots/neutral-analysis-bot/database.db
chmod 666 /opt/bots/neutral-analysis-bot/database.db
```

### Сервер "зависает"

```bash
# Перезагрузи
reboot
```

Подожди 2 минуты, сервер перезапустится.

---

## 💰 МОНИТОРИНГ РАСХОДОВ

### Где смотреть

1. Личный кабинет Timeweb
2. "Баланс" → "История операций"

**Списание:**
- VPS S: 150₽/мес (5₽/день)
- Автоматически со счета

**Автопополнение:**
- Можно настроить автопополнение
- "Баланс" → "Автоплатеж"

---

## 🔒 БЕЗОПАСНОСТЬ

### Сменить root пароль

```bash
passwd root
```

Введи новый пароль дважды.

### Настроить firewall (опционально)

```bash
# Установить ufw
apt install ufw

# Разрешить SSH
ufw allow 22/tcp

# Включить firewall
ufw enable
```

### Обновления системы

```bash
# Автообновления
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## ✅ ЧЕКЛИСТ УСПЕХА

После выполнения всех шагов:

- [ ] Аккаунт на Timeweb Cloud создан
- [ ] VPS создан и оплачен
- [ ] Подключение по SSH работает
- [ ] Python и зависимости установлены
- [ ] Проект склонирован с GitHub
- [ ] .env файл настроен
- [ ] Systemd сервис создан
- [ ] Бот запущен и работает 24/7
- [ ] Тест в Telegram прошёл успешно

---

## 🎉 ГОТОВО!

Твой бот теперь работает на сервере 24/7!

**Стоимость:** 150₽/мес  
**Uptime:** 99.9%  
**Автоперезапуск:** Да

**Следующие шаги:**
1. Настрой автодеплой (Шаг 10)
2. Добавь реальные платежи (ЮKassa)
3. Начни привлекать пользователей!

---

## 📞 ПОДДЕРЖКА

**Timeweb поддержка:**
- Онлайн чат на сайте
- Email: support@timeweb.ru
- Telegram: @timeweb_support

**Наша поддержка:**
- Telegram: @your_support

---

**Удачи с запуском!** 🚀
