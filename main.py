import asyncio
from pprint import pprint
import psycopg
import random
import selectors
import sys
from typing import Dict
import vkbottle as vk
from vkbottle import GroupEventType
from vkbottle.bot import Message

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import MetaData, create_engine, text

from bot import bot
from db_engine import sync_engine, async_engine, async_session_maker
from globals import DB_URL, BOT_TOKEN
from models import *
from keyboards import *
from states import UserStates

# Задачи в процессе создания
tasks_in_creation: Dict[int, Dict[str, str]] = {}

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

@bot.on.message(text='Вернуться в главное меню')
@bot.on.message(payload={'cmd': 'main_menu'})
async def main_menu_return_handler(message: Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
    print(await bot.state_dispenser.get(peer_id=message.peer_id))
    await message.answer(
        "Вы вышли в главное меню",
        keyboard=main_menu_keyboard
    )

@bot.on.message(text='/start')
async def start(message: Message):
    # Проверка на то, что пользователь уже есть в БД
    if not await check_user_reg(message.from_id):
        # Если нет
        # async with async_engine.begin() as aconn:
        #     user = await bot.api.users.get(user_ids=[message.from_id])
        #     first_name = user[0].first_name
        #     last_name = user[0].last_name
        #     await aconn.execute(
        #         text('INSERT INTO users(id, first_name, last_name) VALUES (:user_id, :first_name, :last_name)'),
        #         {
        #             'user_id': message.from_id,
        #             'first_name': first_name,
        #             'last_name': last_name
        #         }
        #     )
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
    await message.answer('Добро пожаловать в бота', keyboard=main_menu_keyboard)

@bot.on.message()
async def unknown_message(message: Message):
    user = await bot.api.users.get(user_ids=[1106823933])
    # pprint(user, indent=3, width=40)
    await message.answer(
        "Неизвестное сообщение. "
        "Напишите /start для входа в главное меню"
    )

if __name__ == '__main__':
    # print(psycopg.pq.__impl__)
    if sys.platform == 'win32':
        # Обновление схемы базы данных
        # asyncio.run(
        #     recreate_db(),
        #     loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        # )
        # asyncio.set_event_loop(asyncio.SelectorEventLoop())
        bot.loop_wrapper.loop = asyncio.SelectorEventLoop()
        print(bot.labeler.message_view.handlers)
        bot.run_forever()
    else:
        # asyncio.run(main())
        bot.run_forever()
