from __future__ import annotations
from vkbottle.bot import MessageEvent
from vkbottle.tools.formatting import Format, bold, italic
from typing import TYPE_CHECKING, Dict, List
from sqlalchemy import select, and_

from bot import bot, tasks_list_params
from db_engine import async_session_maker
from models import TasksModel, TypeEnum, DifficulcyEnum

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

async def get_task(user_id: int) -> TasksModel:
    async with async_session_maker() as session:
        stmt = (
            select(TasksModel)
            .where(
                and_(
                    TasksModel.user_id==user_id,
                    TasksModel.type.in_(tasks_list_params[user_id]['types']),
                    TasksModel.difficulcy.in_(tasks_list_params[user_id]['difficulties'])
                )
            )
            .order_by(TasksModel.id.asc())
            .limit(1)
            .offset(tasks_list_params[user_id]['curr_offset'])
        )
        result = await session.execute(stmt)
        task: TasksModel = result.scalar()
        return task
    
def show_task(task: TasksModel) -> str:
    str_task_info = (
        f'Описание: {task.description if task.description else 'Нет описания'}\n'
        f'Тип задачи: {ru_types[task.type.value]}\n'
        f'Сложность задачи: {ru_difficulties[task.difficulcy.value]}\n\n'
    )
    str_task_info = bold(f'{task.title}\n\n') + str_task_info + italic('test')
    return str_task_info

# Отправляет пустой ответ на нажатие callback кнопки (чтобы кнопка снова стала кликабельной)
async def empty_callback_answer(event: MessageEvent):
    await bot.api.messages.send_message_event_answer(
        event_id=event.event_id,
        peer_id=event.peer_id,
        user_id=event.user_id,
        event_data=None
    )

# Переводы сложностей задач на английский
ru_types = {'reusable': 'Постоянная', 'disposable': 'Одноразовая'}

# Переводы сложностей задач на русский
ru_difficulties = {'very_easy': 'Очень легко', 'easy': 'Легко', 'medium': 'Средне', 'hard': 'Сложно', 'very_hard': 'Очень сложно'}