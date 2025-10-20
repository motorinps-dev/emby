#!/bin/bash

echo "🚀 Установка Telegram бота для Emby на локальный сервер"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

echo "✅ Python $(python3 --version) найден"

# Проверка pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip."
    exit 1
fi

echo "✅ pip найден"
echo ""

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Скопируйте .env.example в .env:"
echo "   cp .env.example .env"
echo ""
echo "2. Отредактируйте .env и заполните все переменные:"
echo "   nano .env"
echo ""
echo "3. Запустите бота:"
echo "   source venv/bin/activate"
echo "   python bot.py"
echo ""
echo "4. Для автозапуска при загрузке системы:"
echo "   sudo ./install_service.sh"
echo ""
