from sqlalchemy import select
import vkbottle as vk
from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle.tools.formatting import bold, Format

from bot import bot
from logic import get_full_name
from states import UserStates
from keyboards import KeyboardCreator as KC
from db_engine import async_session_maker
from models import UserModel, UserCountersModel

profile_labeler: BotLabeler = BotLabeler()

@profile_labeler.message(payload={'cmd': 'my_profile'})
async def profile_enter_handler(message: Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_PROFILE)
    await message.answer(
        "Ваш профиль",
        keyboard=KC.back_main_menu_keyboard()
    )
    await message.answer(
        await get_profile_info(message.from_id)
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
        (
            '\n\n'
            f'Количество опыта: {user.current_xp}\n'
            f'Выполнено очень лёгких задач: {user_counters.very_easy}\n'
            f'Выполнено лёгких задач: {user_counters.easy}\n'
            f'Выполнено средних задач: {user_counters.medium}\n'
            f'Выполнено сложных задач: {user_counters.hard}\n'
            f'Выполнено очень сложных задач: {user_counters.very_hard}\n'
        )
    )
    return profile_info

