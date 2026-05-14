from sqlalchemy import select, func
from typing import List
import vkbottle as vk
from vkbottle import AndRule, OrRule
from vkbottle.bot import BotLabeler, Message, MessageEvent, rules

from bot import bot, service_api
from db_engine import async_session_maker
from keyboards import KeyboardCreator as KC
from logic import (
    get_full_name, get_level, 
    get_leaderboard_row, empty_callback_answer)
from models import UserModel
from states import UserStates


leaderboard_labeler: BotLabeler = BotLabeler()

# Правило для проверки состояния пользователя при работе с MessageEvent
class CustomStateRule(vk.ABCRule[MessageEvent]):
    def __init__(self, state):
        self.state = state

    async def check(self, event: MessageEvent):
        curr_state = await bot.state_dispenser.get(event.peer_id)
        return curr_state.state == self.state

leaderboard_labeler.custom_rules['custom_state'] = CustomStateRule

# Переход на страницу таблицы лидеров
@leaderboard_labeler.message(
    payload={'cmd': 'leaderboard'}
)
async def leaderboard_enter_handler(message: Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_LEADERBOARD_GLOBAL)
    answer = await get_global_leaderboard(message.from_id)
    print(answer, 'это answer в обработчике входа в таблицу лидеров')
    await message.answer(
        "Таблица лидеров",
        keyboard=KC.back_main_menu_keyboard()
    )
    await message.answer(
        answer,
        keyboard=KC.in_leaderboard_keyboard()
    )

# Обработчик для вывода таблиц лидеров друзей
@leaderboard_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    OrRule(
        AndRule(
            rules.PayloadRule({'leaderboard': 'friends'}),
            CustomStateRule(UserStates.IN_LEADERBOARD_GLOBAL)
        ),
        AndRule(
            rules.PayloadRule({'leaderboard': 'global'}),
            CustomStateRule(UserStates.IN_LEADERBOARD_FRIENDS)
        )
    )
)
async def leaderboard_in_handler(event: MessageEvent):
    if event.payload == {'leaderboard': 'global'}:
        print('попытка вывести global')
        await bot.state_dispenser.set(peer_id=event.peer_id, state=UserStates.IN_LEADERBOARD_GLOBAL)
        await bot.api.messages.edit(
            event.peer_id,
            cmid=event.conversation_message_id,
            message=await get_global_leaderboard(event.user_id),
            keyboard=KC.in_leaderboard_keyboard('global')
        )
        print('вывод global')
    else:
        await bot.state_dispenser.set(peer_id=event.peer_id, state=UserStates.IN_LEADERBOARD_FRIENDS)
        # Переделать под таблицу лидеров друзей
        print('попытка вывести friends')
        await bot.api.messages.edit(
            event.peer_id,
            cmid=event.conversation_message_id,
            message=await get_friends_leaderboard(event.user_id),
            keyboard=KC.in_leaderboard_keyboard('friends')
        )
        print('вывод friends')
    await empty_callback_answer(event)

# Выдает глобальную таблицу лидеров
async def get_global_leaderboard(user_id: int):
    answer = ''
    async with async_session_maker() as session:
        stmt = (
            select(UserModel)
            .where(UserModel.is_public == True)
            .union(
                select(UserModel)
                .where(UserModel.id==user_id)
            )
            .order_by(UserModel.current_xp.desc())
            .limit(15)
        )
        result = await session.execute(stmt)
        users: List[UserModel] = result.all()
        user_in_leaderboard = False
        for idx, user in enumerate(users):
            if user.id == user_id:
                user_in_leaderboard = True
            answer = answer + get_leaderboard_row(user, idx)
        if not user_in_leaderboard:
            sub_stmt = (
                select(UserModel, func.row_number().over(order_by=UserModel.current_xp.desc()).label('rank'))
            )
            stmt = (
                select('*')
                .select_from(sub_stmt)
                .where(sub_stmt.c.id == user_id)
            )
            curr_user = (await session.execute(stmt)).fetchone()
            print(curr_user, type(curr_user))
            answer =  answer + '➖➖➖➖➖➖➖➖➖➖➖➖\n' + get_leaderboard_row(curr_user, curr_user.rank - 1) + '\n'
    return answer

# Выдает таблицу лидеров друзей (включая пользователя)
async def get_friends_leaderboard(user_id: int):
    answer = ''
    friends: List[int] = []
    try:
        friends = (await service_api.friends.get(user_id=user_id)).items
    except vk.exception_factory.base_exceptions.VKAPIError_30:
        print('отловилась ошибка приватного профиля')
        answer = answer + 'Не удалось получить ваш список друзей. Сделайте профиль открытым (публичным) и повторите попытку\n\n'
        friends = []
    friends.append(user_id)
    async with async_session_maker() as session:
        stmt = (
            select(UserModel.id, UserModel.first_name, UserModel.last_name, UserModel.current_xp)
            .where(UserModel.id.in_(friends))
            .order_by(UserModel.current_xp.desc())
            .limit(15)
        )
        result = await session.execute(stmt)
        users: List[UserModel] = result.all()
        user_in_leaderboard = False
        for idx, user in enumerate(users):
            if user.id == user_id:
                user_in_leaderboard = True
            answer = answer + get_leaderboard_row(user, idx)
        if not user_in_leaderboard:
            sub_stmt = (
                select(UserModel, func.row_number().over(order_by=UserModel.current_xp.desc()).label('rank'))
            )
            stmt = (
                select('*')
                .select_from(sub_stmt)
                .where(sub_stmt.c.id == user_id)
            )
            curr_user = (await session.execute(stmt)).fetchone()
            print(curr_user, type(curr_user))
            answer =  answer + '➖➖➖➖➖➖➖➖➖➖➖➖\n' + get_leaderboard_row(curr_user, curr_user.rank - 1) + '\n'
    return answer
