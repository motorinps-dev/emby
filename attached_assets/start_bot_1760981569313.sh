#!/bin/bash

# Скрипт для установки зависимостей и запуска Telegram бота

echo "🤖 Установка и запуск Telegram бота для управления Emby"
echo "=========================================="

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не установлен. Пожалуйста, установите Python 3.11 или выше."
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"

# Переходим в директорию бота
cd bot

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Создаю из .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📝 Файл .env создан. Пожалуйста, отредактируйте его и укажите:"
        echo "   - TELEGRAM_BOT_TOKEN (получите у @BotFather)"
        echo "   - EMBY_SERVER_URL (адрес вашего Emby сервера)"
        echo "   - EMBY_API_KEY (API ключ из настроек Emby)"
        echo "   - FIRST_ADMIN_ID (ваш Telegram ID, узнайте у @userinfobot)"
        echo ""
        echo "После настройки запустите скрипт снова."
        exit 1
    else
        echo "❌ Файл .env.example не найден!"
        exit 1
    fi
fi

# Загружаем переменные окружения
export $(grep -v '^#' .env | xargs)

# Проверяем наличие необходимых переменных
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" == "your_telegram_bot_token_here" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN не настроен в файле .env"
    exit 1
fi

if [ -z "$EMBY_SERVER_URL" ] || [ "$EMBY_SERVER_URL" == "http://localhost:8096" ]; then
    echo "⚠️  Используется стандартный EMBY_SERVER_URL. Убедитесь, что это правильно."
fi

if [ -z "$EMBY_API_KEY" ] || [ "$EMBY_API_KEY" == "your_emby_api_key_here" ]; then
    echo "❌ EMBY_API_KEY не настроен в файле .env"
    exit 1
fi

echo "✅ Переменные окружения загружены"

# Проверяем наличие виртуального окружения
if [ ! -d "../.pythonlibs" ]; then
    echo "⚠️  Виртуальное окружение не найдено."
    echo "📦 Устанавливаю зависимости..."
    
    # Устанавливаем зависимости через uv (если доступен) или pip
    if command -v uv &> /dev/null; then
        echo "Использую uv для установки зависимостей..."
        cd ..
        uv pip install -r bot/requirements.txt
        cd bot
    elif command -v pip3 &> /dev/null; then
        echo "Использую pip для установки зависимостей..."
        pip3 install -r requirements.txt
    else
        echo "❌ Не найден ни uv, ни pip!"
        exit 1
    fi
fi

echo "✅ Зависимости установлены"
echo ""
echo "🚀 Запускаю бота..."
echo "=========================================="
echo ""

# Запускаем бота
python3 bot.py
