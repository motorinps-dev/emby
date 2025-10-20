#!/bin/bash

# Этот скрипт создает systemd service для автозапуска бота

if [ "$EUID" -ne 0 ]; then 
    echo "❌ Запустите этот скрипт с sudo"
    exit 1
fi

# Получаем текущую директорию и пользователя
CURRENT_DIR=$(pwd)
CURRENT_USER=$(logname)

echo "🔧 Создание systemd service для Emby Telegram Bot..."
echo "📁 Директория: $CURRENT_DIR"
echo "👤 Пользователь: $CURRENT_USER"

# Создаем service файл
cat > /etc/systemd/system/emby-telegram-bot.service <<EOF
[Unit]
Description=Emby Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service файл создан: /etc/systemd/system/emby-telegram-bot.service"

# Перезагружаем systemd
systemctl daemon-reload

echo ""
echo "✅ Готово! Доступные команды:"
echo ""
echo "  Запустить бота:"
echo "    sudo systemctl start emby-telegram-bot"
echo ""
echo "  Остановить бота:"
echo "    sudo systemctl stop emby-telegram-bot"
echo ""
echo "  Перезапустить бота:"
echo "    sudo systemctl restart emby-telegram-bot"
echo ""
echo "  Включить автозапуск при загрузке:"
echo "    sudo systemctl enable emby-telegram-bot"
echo ""
echo "  Посмотреть статус:"
echo "    sudo systemctl status emby-telegram-bot"
echo ""
echo "  Посмотреть логи:"
echo "    sudo journalctl -u emby-telegram-bot -f"
echo ""
