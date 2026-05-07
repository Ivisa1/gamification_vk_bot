import vkbottle as vk
from vkbottle.bot import BotLabeler
from sqlalchemy import select
from typing import List

from bot import bot
from db_engine import async_session_maker
from logic import get_full_name, get_level
from states import UserStates
from keyboards import back_main_menu_keyboard
from models import UserModel

leaderboard_labeler: BotLabeler = BotLabeler()

# Переход на страницу таблицы лидеров
@leaderboard_labeler.message(payload={'cmd': 'leaderboard'})
async def leaderboard_enter_handler(message: vk.Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_LEADERBOARD)
    answer = ''
    async with async_session_maker() as session:
        stmt = select(UserModel.id, UserModel.first_name, UserModel.last_name, UserModel.current_xp).order_by(UserModel.current_xp.desc()).limit(15)
        result = await session.execute(stmt)
        users: List[UserModel] = result.all()
        print(users)
        for idx, user in enumerate(users):
            answer = (
                answer + 
                '%i. [id%i|%s] - %i очков опыта\n' % 
                (idx+1, user.id, get_full_name(user.first_name, user.last_name), user.current_xp)
            )
    await message.answer(
        answer,
        keyboard=back_main_menu_keyboard
    )