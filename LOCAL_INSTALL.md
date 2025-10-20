# Инструкция по установке бота на локальный сервер с Emby

## Требования

- Linux сервер (Ubuntu, Debian, CentOS и т.д.) или Windows с Python
- Python 3.8 или выше
- Доступ к серверу по SSH (для Linux) или RDP (для Windows)
- Emby Server, работающий на том же сервере или в локальной сети

## Установка на Linux (рекомендуется)

### 1. Скачайте файлы проекта

Вариант A: Скачать с Replit вручную

1. Скачайте все файлы проекта с Replit:
   - bot.py
   - database.py
   - emby_api.py
   - requirements.txt
   - .env.example
   - install_local.sh
   - install_service.sh

2. Загрузите их на сервер через SFTP/SCP или создайте папку:

```bash
mkdir -p /opt/emby-telegram-bot
cd /opt/emby-telegram-bot
# Скопируйте файлы сюда
```

Вариант B: Клонировать из Git (если выложили в репозиторий)

```bash
git clone <ваш-репозиторий>
cd emby-telegram-bot
```

### 2. Установите зависимости

```bash
# Сделайте скрипт исполняемым
chmod +x install_local.sh

# Запустите установку
./install_local.sh
```

Или вручную:

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте файл
nano .env
```

Заполните все переменные:

```env
TELEGRAM_BOT_TOKEN=7364573428:AAEmMKRxPLrEjLLaaXDvTQicrXzoA5iQbkA
EMBY_SERVER_URL=http://192.168.1.60:8096
EMBY_API_KEY=ваш_api_ключ_emby
FIRST_ADMIN_ID=6321055926
SESSION_SECRET=любая_случайная_строка
```

### 4. Запустите бота

Для тестирования (вручную):

```bash
source venv/bin/activate
python bot.py
```

Для постоянной работы (systemd service):

```bash
# Сделайте скрипт исполняемым
chmod +x install_service.sh

# Установите service
sudo ./install_service.sh

# Запустите бота
sudo systemctl start emby-telegram-bot

# Включите автозапуск при загрузке
sudo systemctl enable emby-telegram-bot

# Проверьте статус
sudo systemctl status emby-telegram-bot

# Смотрите логи в реальном времени
sudo journalctl -u emby-telegram-bot -f
```

## Установка на Windows

### 1. Установите Python

Скачайте Python 3.8+ с [python.org](https://www.python.org/downloads/)

### 2. Скачайте файлы проекта

Создайте папку, например `C:\emby-telegram-bot` и поместите туда все файлы.

### 3. Установите зависимости

Откройте PowerShell или CMD в папке проекта:

```cmd
# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
```

### 4. Создайте файл .env

Скопируйте `.env.example` в `.env` и заполните переменные:

```env
TELEGRAM_BOT_TOKEN=ваш_токен
EMBY_SERVER_URL=http://localhost:8096
EMBY_API_KEY=ваш_api_ключ
FIRST_ADMIN_ID=ваш_telegram_id
```

### 5. Запустите бота

```cmd
venv\Scripts\activate
python bot.py
```

### 6. Автозапуск на Windows (опционально)

Вариант A: Создайте bat файл `start_bot.bat`:

```bat
@echo off
cd C:\emby-telegram-bot
call venv\Scripts\activate
python bot.py
pause
```

Добавьте его в автозагрузку через Планировщик задач.

Вариант B: Используйте NSSM (Non-Sucking Service Manager):

```cmd
# Скачайте NSSM с nssm.cc
nssm install EmbyTelegramBot "C:\emby-telegram-bot\venv\Scripts\python.exe" "C:\emby-telegram-bot\bot.py"
nssm start EmbyTelegramBot
```

## Как получить необходимые данные

### TELEGRAM_BOT_TOKEN

1. Откройте Telegram и найдите @BotFather
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

### EMBY_API_KEY

1. Откройте Emby Server Dashboard
2. Settings → Advanced → API Keys
3. Нажмите "New API Key"
4. Скопируйте ключ

### FIRST_ADMIN_ID

1. Откройте Telegram и найдите @userinfobot
2. Отправьте `/start`
3. Скопируйте ваш ID

## Управление ботом

### Просмотр логов (Linux)

```bash
# Логи systemd
sudo journalctl -u emby-telegram-bot -f

# Или если запущен вручную - смотрите в консоль
```

### Остановка/Перезапуск (Linux)

```bash
# Остановить
sudo systemctl stop emby-telegram-bot

# Перезапустить
sudo systemctl restart emby-telegram-bot

# Статус
sudo systemctl status emby-telegram-bot
```

### Обновление бота

```bash
# Остановите бота
sudo systemctl stop emby-telegram-bot

# Обновите файлы (bot.py, database.py, emby_api.py)
# Если есть новые зависимости:
source venv/bin/activate
pip install -r requirements.txt

# Запустите снова
sudo systemctl start emby-telegram-bot
```

## Проверка работы

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Вы должны увидеть главное меню
4. Нажмите "⚙️ Настройки" → "🔌 Проверить подключение к Emby"
5. Должно показать "✅ Подключение успешно!"

## Устранение неполадок

### Бот не запускается

```bash
# Проверьте логи
sudo journalctl -u emby-telegram-bot -n 50

# Проверьте файл .env
cat .env

# Проверьте права
ls -la
```

### Не подключается к Emby

- Проверьте URL Emby в .env
- Убедитесь что Emby Server запущен
- Проверьте API ключ
- Попробуйте открыть URL в браузере с того же сервера

### База данных не создается

- Проверьте права на запись в директории
- Убедитесь что SQLite установлен (обычно идет с Python)

## Безопасность

- Файл `.env` содержит секретные данные - не публикуйте его
- Ограничьте доступ к файлам бота:
  ```bash
  chmod 600 .env
  chmod 700 bot.py database.py emby_api.py
  ```
- Регулярно обновляйте зависимости:
  ```bash
  pip install --upgrade -r requirements.txt
  ```

## Резервное копирование

Регулярно делайте backup базы данных:

```bash
# Создать backup
cp emby_bot.db emby_bot.db.backup

# Или с датой
cp emby_bot.db emby_bot.db.$(date +%Y%m%d)
```
