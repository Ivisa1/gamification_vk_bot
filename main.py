import asyncio
# import psycopg
# import random
import selectors
import sys
import os
import vkbottle as vk
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

from sqlalchemy import MetaData, text, select

from bot import bot, tasks_in_creation, tasks_list_params
from db_engine import sync_engine, async_engine, async_session_maker
from globals import DB_URL, BOT_TOKEN
from logic import empty_callback_answer
from models import *
from keyboards import KeyboardCreator as KC
from states import UserStates

# Константы для режимов работы
POLLING_METHODS = {
    'longpoll': 'LongPollAPI',
    'callback': 'CallbackAPI (Webhook)'
}

# Функция пересоздания БД
async def recreate_db():
    with sync_engine.begin() as conn:
        # Удаление таблиц
        metadata = MetaData()
        metadata.reflect(bind=sync_engine)
        metadata.drop_all(bind=sync_engine)
        # Создание таблиц
        BaseModel.metadata.create_all(bind=sync_engine)

async def check_user_reg(user_id: int):
    async with async_engine.begin() as aconn:
        result = await aconn.execute(
            text('SELECT * FROM users WHERE id = :user_id'),
            {'user_id': user_id}
        )
        user = result.scalar_one_or_none()
        
        # 3. Печатаем и возвращаем результат
        print(user)
        return bool(user)

@bot.loop_wrapper.interval(seconds=20000)
async def interval_func():
    async with async_engine.begin() as aconn:
        res = await aconn.execute(text('SELECT VERSION();'))
        print(res.all())
    print('Я выполнилась')

@bot.on.message(payload={'cmd': 'main_menu'})
async def main_menu_return_handler(message: Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
    await message.answer(
        "Вы вышли в главное меню",
        keyboard=KC.main_menu_keyboard()
    )
    user_id = message.from_id
    tasks_in_creation.pop(user_id, None)

@bot.on.message(text='/start')
async def start(message: Message):
    # Проверка на то, что пользователь уже есть в БД
    if not await check_user_reg(message.from_id):
        async with async_session_maker.begin() as session:
            user_data = await bot.api.users.get(user_ids=[message.from_id])
            first_name = user_data[0].first_name
            last_name = user_data[0].last_name
            user = UserModel(
                id=message.from_id,
                first_name=first_name,
                last_name=last_name,
                
            )
            session.add(user)
            await session.flush()
            user_counters = UserCountersModel(
                id=message.from_id
            )
            session.add(user_counters)
            print('Выполнилось без ошибок')
            print(user.first_name, user.last_name)
            
            # await session.commit()
            
            # aconn.execute()
    user_id = message.from_id
    tasks_in_creation.pop(user_id, None)
    tasks_list_params.pop(user_id, None)
    await message.answer('Добро пожаловать в бота', keyboard=KC.main_menu_keyboard())

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
async def unknown_event(event: MessageEvent):
    asyncio.sleep(0.4)
    await empty_callback_answer(event)

@bot.on.message()
async def unknown_message(message: Message):
    print(message)
    user = await bot.api.users.get(user_ids=[1106823933])
    # pprint(user, indent=3, width=40)
    await message.answer(
        "Неизвестное сообщение. "
        "Напишите /start для перезапуска бота и выхода в главное меню"
    )

# ============== ЗАПУСК БОТА ==============

def get_polling_method() -> str:
    """
    Получить метод работы бота из переменных окружения или интерактивного выбора.
    
    Приоритет:
    1. Переменная окружения POLLING_METHOD
    2. Интерактивный выбор (если не установлена переменная окружения)
    
    Returns:
        'longpoll' или 'callback'
    """
    method = os.getenv('POLLING_METHOD', '').lower()
    
    if method in POLLING_METHODS:
        return method
    
    # Интерактивный выбор
    print("\n" + "="*50)
    print("ВЫБОР МЕТОДА РАБОТЫ БОТА")
    print("="*50)
    print("Доступные методы работы:")
    print("1 - LongPollAPI (длительное опрашивание)")
    print("2 - CallbackAPI (Webhook)")
    print("="*50)
    
    while True:
        choice = input("\nВыберите метод (1 или 2): ").strip()
        if choice == '1':
            return 'longpoll'
        elif choice == '2':
            return 'callback'
        else:
            print("❌ Неверный выбор. Введите 1 или 2.")

def run_longpoll():
    """Запуск бота с использованием LongPollAPI"""
    print("\n" + "="*50)
    print(f"🚀 Запуск бота в режиме: {POLLING_METHODS['longpoll']}")
    print("="*50)
    print("Бот ожидает сообщений через LongPollAPI...")
    print("Для остановки нажмите Ctrl+C")
    print("="*50 + "\n")
    
    if sys.platform == 'win32':
        # Для Windows используем SelectorEventLoop
        bot.loop_wrapper.loop = asyncio.SelectorEventLoop()
    
    bot.run_forever()

def run_callback():
    """Запуск бота с использованием CallbackAPI (Webhook)"""
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("WEBHOOK_PORT", 8080))
    path = os.getenv("WEBHOOK_PATH", "/")
    base_url = os.getenv("BASE_URL")
    secret_key = os.getenv("WEBHOOK_SECRET")
    
    print("\n" + "="*50)
    print(f"🚀 Запуск бота в режиме: {POLLING_METHODS['callback']}")
    print("="*50)
    
    if not base_url:
        print("❌ Ошибка: переменная окружения BASE_URL не задана.")
        print("   Укажите публичный URL вашего сервера.")
        print("\nПример:")
        print("   export BASE_URL=https://example.com")
        sys.exit(1)
    
    if not secret_key:
        print("⚠️  Предупреждение: переменная окружения WEBHOOK_SECRET не задана.")
        print("   Рекомендуется установить секретный ключ для безопасности.")
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Path: {path}")
    print(f"Webhook URL: {base_url}{path}")
    print("="*50)
    print("Сервер слушает входящие события от VK API...")
    print("Для остановки нажмите Ctrl+C")
    print("="*50 + "\n")
    
    # Запускаем сервер с вебхуком
    bot.run_webhook(
        host=host,
        port=port,
        path=path,
        webhook_settings={
            "url": f"{base_url}{path}",
            "secret": secret_key
        }
    )

if __name__ == '__main__':
    polling_method = get_polling_method()
    
    if polling_method == 'longpoll':
        run_longpoll()
    elif polling_method == 'callback':
        run_callback()