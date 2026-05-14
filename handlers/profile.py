from sqlalchemy import select
import vkbottle as vk
from vkbottle.bot import BotLabeler, Message, MessageEvent, rules
from vkbottle.tools.formatting import bold, Format, italic

from bot import bot
from database import get_user
from logic import (
    get_full_name,
    get_level,
    get_need_xp_for_next_level,
    get_curr_xp_for_next_level
)
from states import UserStates
from keyboards import KeyboardCreator as KC
from database import get_user
from db_engine import async_session_maker
from models import UserModel, UserCountersModel

profile_labeler: BotLabeler = BotLabeler()

class CustomStateRule(vk.ABCRule[MessageEvent]):
    def __init__(self, state):
        self.state = state

    async def check(self, event: MessageEvent):
        curr_state = await bot.state_dispenser.get(event.peer_id)
        return curr_state.state == self.state

profile_labeler.custom_rules['custom_state'] = CustomStateRule

@profile_labeler.message(payload={'cmd': 'my_profile'})
async def profile_enter_handler(message: Message):
    user: UserModel = await get_user(message.from_id)
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_PROFILE)
    await message.answer(
        "👤 Ваш профиль",
        keyboard=KC.back_main_menu_keyboard()
    )
    await message.answer(
        await get_profile_info(message.from_id),
        keyboard=KC.profile_keyboard(user.is_public)
    )

@profile_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadContainsRule({'cmd': 'change_visibility'}),
    CustomStateRule(UserStates.IN_PROFILE)
)
async def change_visibility_handler(event: MessageEvent):
    user_id = event.peer_id
    user: UserModel = await get_user(user_id)
    async with async_session_maker() as session:
        session.add(user)
        if user:
            user.is_public = not user.is_public
            await session.commit()
    await event.edit_message(
        await get_profile_info(user_id),
        keyboard=KC.profile_keyboard(user.is_public)
    )

async def get_profile_info(user_id: int):
    user: UserModel | None = None
    user_counters: UserCountersModel | None = None
    profile_info: str | Format = ''
    async with async_session_maker() as session:
        stmt = (
            select(UserModel)
            .where(UserModel.id==user_id)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        stmt = (
            select(UserCountersModel)
            .where(UserCountersModel.id==user_id)
        )
        result = await session.execute(stmt)
        user_counters = result.scalar_one_or_none()
    profile_info = (
        bold(get_full_name(user.first_name, user.last_name)) +
        italic(
            (
                '\n\n'
                f'🎓 Уровень {get_level(user.current_xp)}\n'
                f'⭐ {get_curr_xp_for_next_level(user.current_xp)}/{get_need_xp_for_next_level(get_level(user.current_xp))} опыта до следующего уровня\n\n'
            )
        ) +
        (
            f'😄 Выполнено очень лёгких задач: {user_counters.very_easy}\n'
            f'🙂 Выполнено лёгких задач: {user_counters.easy}\n'
            f'😐 Выполнено средних задач: {user_counters.medium}\n'
            f'😬 Выполнено сложных задач: {user_counters.hard}\n'
            f'🤯 Выполнено очень сложных задач: {user_counters.very_hard}\n'
        )
    )
    return profile_info

