from __future__ import annotations
from vkbottle.bot import MessageEvent
from typing import TYPE_CHECKING
from sqlalchemy import select, and_

from bot import bot
from db_engine import async_session_maker
from models import TasksModel, TypeEnum

if TYPE_CHECKING:
    from models import UserModel

# Получает текущий уровень пользователя на основе его опыта
def get_level(xp: int):
    pass

# Формирует строку Имя Фамилия
def get_full_name(first_name: str, last_name: str):
    return f'{first_name} {last_name}'

# Метод формирует одну строку для таблицы лидеров
def get_leaderboard_row(user: UserModel, idx: int):
    return (
        '%i. [id%i|%s] - %i очков опыта\n' % 
        (idx+1, user.id, get_full_name(user.first_name, user.last_name), user.current_xp)
    )

async def get_task(user_id: int, curr_offset: int, type: TypeEnum):
    async with async_session_maker() as session:
        stmt = select(TasksModel).where(and_(TasksModel.user_id==user_id, TasksModel.type==TypeEnum)).limit(1).offset(curr_offset)

# Отправляет пустой ответ на нажатие callback кнопки (чтобы кнопка снова стала кликабельной)
async def empty_callback_answer(event: MessageEvent):
    await bot.api.messages.send_message_event_answer(
        event_id=event.event_id,
        peer_id=event.peer_id,
        user_id=event.user_id,
        event_data=None
    )