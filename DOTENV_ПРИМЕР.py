# Пример интеграции python-dotenv в main.py
# Добавьте эту строку в самое начало main.py (после импортов):
#
# from dotenv import load_dotenv
# load_dotenv()  # Загружает переменные из .env файла
#
# Затем скопируйте .env.example в .env:
#   cp .env.example .env
#
# И отредактируйте .env с нужными значениями
#
# Установите python-dotenv:
#   pip install python-dotenv

# ============ ПРИМЕР ИСПОЛЬЗОВАНИЯ ============

from dotenv import load_dotenv
import os

# Загрузить переменные из .env файла
load_dotenv()

# Теперь можете использовать os.getenv() как обычно
POLLING_METHOD = os.getenv('POLLING_METHOD')
BASE_URL = os.getenv('BASE_URL')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

print(f"Метод: {POLLING_METHOD}")
print(f"Base URL: {BASE_URL}")
print(f"Secret: {WEBHOOK_SECRET}")
