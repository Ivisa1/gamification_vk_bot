from __future__ import annotations
from vkbottle.bot import MessageEvent
from vkbottle.tools.formatting import Format, bold, italic
from typing import TYPE_CHECKING, Dict, List
from sqlalchemy import select, and_

from bot import bot, tasks_list_params
from db_engine import async_session_maker
from globals import STEP_LEVEL # 300
from models import TasksModel, UserCountersModel, TypeEnum, DifficultyEnum

if TYPE_CHECKING:
    from models import UserModel

# Получает текущий уровень пользователя на основе его опыта
def get_level(xp: int):
    return int(
        (STEP_LEVEL + (STEP_LEVEL**2 + 4 * STEP_LEVEL * 2 * xp)**0.5) / (2 * STEP_LEVEL)
    )

# Получает количество опыта, необходимое для достижения следующего уровня
def get_need_xp_for_next_level(level: int):
    return STEP_LEVEL * level

# Получает общее количество опыта, необходимое для достижения следующего уровня
def get_all_xp_on_this_level(level: int):
    return int(
        ((STEP_LEVEL * (level - 1)) / 2) * level
    )

def get_curr_xp_for_next_level(xp: int):
    this_level_xp = get_all_xp_on_this_level(get_level(xp))
    return xp - this_level_xp

async def get_user(user_id: int):
    async with async_session_maker() as session:
        stmt = (
            select(UserModel)
            .where(UserModel.id==user_id)
        )

# Формирует строку Имя Фамилия
def get_full_name(first_name: str, last_name: str):
    return f'{first_name} {last_name}'

# Метод формирует одну строку для таблицы лидеров
def get_leaderboard_row(user: UserModel, idx: int):
    sticker_place = '🥇 ' if idx==0 else '🥈 ' if idx==1 else '🥉 ' if idx==2 else '🎖️ ' if idx > 14 else '   '
    return (
        '%s%i. [id%i|%s] - %i уровень\n'
        % (sticker_place, idx+1, user.id, get_full_name(user.first_name, user.last_name), get_level(user.current_xp))
    )

async def get_task(user_id: int) -> TasksModel:
    async with async_session_maker() as session:
        stmt = (
            select(TasksModel)
            .where(
                and_(
                    TasksModel.user_id==user_id,
                    TasksModel.type.in_(tasks_list_params[user_id]['types']),
                    TasksModel.difficulty.in_(tasks_list_params[user_id]['difficulties'])
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
        bold(f'🎯 {task.title}\n\n') +
        'Описание: ' + italic(f'{task.description if task.description else "Нет описания"}\n') +
        'Тип задачи: ' + italic(f'{ru_types[task.type.value]}\n') +
        'Сложность задачи: ' + italic(f'{ru_difficulties[task.difficulty.value]}\n\n')
    )
    return str_task_info

# Отправляет пустой ответ на нажатие callback кнопки (чтобы кнопка снова стала кликабельной)
async def empty_callback_answer(event: MessageEvent):
    await bot.api.messages.send_message_event_answer(
        event_id=event.event_id,
        peer_id=event.peer_id,
        user_id=event.user_id,
        event_data=None
    )

async def add_xp(task: TasksModel):
    amount = how_much_xp(task.difficulty)
    return 

def how_much_xp(difficulty):
    match difficulty:
        case DifficultyEnum.VERY_EASY:
            return 100
        case DifficultyEnum.EASY:
            return 200
        case DifficultyEnum.MEDIUM:
            return 300
        case DifficultyEnum.HARD:
            return 400
        case DifficultyEnum.VERY_HARD:
            return 500

def increment_counter(task: TasksModel, user_counters: UserCountersModel):
    match task.difficulty:
        case DifficultyEnum.VERY_EASY:
            user_counters.very_easy += 1
        case DifficultyEnum.EASY:
            user_counters.easy += 1
        case DifficultyEnum.MEDIUM:
            user_counters.medium += 1
        case DifficultyEnum.HARD:
            user_counters.hard += 1
        case DifficultyEnum.VERY_HARD:
            user_counters.very_hard += 1

# Переводы сложностей задач на английский
ru_types = {'reusable': 'Постоянная', 'disposable': 'Одноразовая'}

# Переводы сложностей задач на русский
ru_difficulties = {'very_easy': 'Очень легко', 'easy': 'Легко', 'medium': 'Средне', 'hard': 'Сложно', 'very_hard': 'Очень сложно'}