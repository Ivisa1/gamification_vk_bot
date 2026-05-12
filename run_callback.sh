#!/bin/bash
# Скрипт для запуска бота в режиме CallbackAPI (Webhook)
# Перед запуском установите переменные окружения!

# Пример настройки (раскомментируйте и заполните):
# export BASE_URL="https://your-domain.com"
# export WEBHOOK_HOST="0.0.0.0"
# export WEBHOOK_PORT="8080"
# export WEBHOOK_PATH="/"
# export WEBHOOK_SECRET="your-secret-key"

export POLLING_METHOD=callback

if [ -z "$BASE_URL" ]; then
    echo "❌ Ошибка: переменная BASE_URL не установлена!"
    echo "Установите её перед запуском:"
    echo "  export BASE_URL=https://your-domain.com"
    exit 1
fi

echo "Запуск бота в режиме CallbackAPI..."
echo "BASE_URL: $BASE_URL"
python main.py
