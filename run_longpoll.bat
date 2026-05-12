@echo off
REM Скрипт для запуска бота в режиме LongPollAPI (Windows)

setlocal enabledelayedexpansion

set POLLING_METHOD=longpoll

echo Запуск бота в режиме LongPollAPI...
python main.py

pause
