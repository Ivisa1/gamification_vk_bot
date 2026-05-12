@echo off
REM Скрипт для запуска бота в режиме CallbackAPI (Webhook) - Windows
REM Перед запуском установите переменные окружения в этом файле!

setlocal enabledelayedexpansion

REM Установите эти переменные перед запуском:
set POLLING_METHOD=callback
set BASE_URL=https://your-domain.com
set WEBHOOK_HOST=0.0.0.0
set WEBHOOK_PORT=8080
set WEBHOOK_PATH=/
set WEBHOOK_SECRET=your-secret-key

if "!BASE_URL!"=="" (
    echo ❌ Ошибка: переменная BASE_URL не установлена!
    echo Установите её в этом файле перед запуском
    pause
    exit /b 1
)

echo Запуск бота в режиме CallbackAPI...
echo BASE_URL: !BASE_URL!
python main.py

pause
