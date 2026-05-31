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
from samples import insert_20_users
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

async def insert_samples():
    await insert_20_users()

# seconds_before_new_day = 86400
# @bot.loop_wrapper.interval(seconds=20000)
# async def interval_func():
#     async with async_engine.begin() as aconn:
#         res = await aconn.execute(text('SELECT VERSION();'))
#         print(res.all())

if __name__ == '__main__':
    # print(psycopg.pq.__impl__)
    if sys.platform == 'win32':
        # Обновление схемы базы данных
        # asyncio.run(
            # recreate_db(),
            # loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        # )
        # asyncio.set_event_loop(asyncio.SelectorEventLoop())
        # asyncio.run(
            # insert_samples(),
            # loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        # )
        bot.loop_wrapper.loop = asyncio.SelectorEventLoop()
        # print(*bot.labeler.message_view.handlers, sep='\n', end='\n')
        # print(*bot.labeler.raw_event_view.handlers.items(), sep='\n', end='\n')
        bot.run_forever()
    else:
        # asyncio.run(main())
        bot.run_forever()
