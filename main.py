import asyncio
# import psycopg
# import random
import selectors
import sys
import vkbottle as vk
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent

from sqlalchemy import MetaData, text, select

from bot import bot, tasks_in_creation, tasks_list_params
from db_engine import sync_engine, async_engine, async_session_maker
from logic import empty_callback_answer
from models import *
from keyboards import KeyboardCreator as KC
from states import UserStates

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
        
        print(user)
        return bool(user)

seconds_before_new_day = 86400
@bot.loop_wrapper.interval(seconds=20000)
async def interval_func():
    async with async_engine.begin() as aconn:
        res = await aconn.execute(text('SELECT VERSION();'))
        print(res.all())

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
        async with async_session_maker() as session:
            print('Регистрация пользователя')
            user_data = await bot.api.users.get(user_ids=[message.from_id])
            first_name = user_data[0].first_name
            last_name = user_data[0].last_name
            user = UserModel(
                id=message.from_id,
                first_name=first_name,
                last_name=last_name,
                current_xp=0
            )
            session.add(user)
            await session.flush()
            user_counters = UserCountersModel(
                id=message.from_id
            )
            session.add(user_counters)
            await session.commit()
            print('Пользователь зарегистрирован')

    user_id = message.from_id
    tasks_in_creation.pop(user_id, None)
    tasks_list_params.pop(user_id, None)
    await message.answer('Добро пожаловать в бота', keyboard=KC.main_menu_keyboard())

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
async def unknown_event(event: MessageEvent):
    await asyncio.sleep(0.4)
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

if __name__ == '__main__':
    # print(psycopg.pq.__impl__)
    if sys.platform == 'win32':
        # Обновление схемы базы данных
        # asyncio.run(
            # recreate_db(),
            # loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        # )
        # asyncio.set_event_loop(asyncio.SelectorEventLoop())
        bot.loop_wrapper.loop = asyncio.SelectorEventLoop()
        bot.run_forever()
    else:
        # asyncio.run(main())
        bot.run_forever()
