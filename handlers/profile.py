from sqlalchemy import select
import vkbottle as vk
from vkbottle.bot import BotLabeler, Message, MessageEvent

from bot import bot
from states import UserStates
from keyboards import back_main_menu_keyboard
from db_engine import async_session_maker
from models import UserModel

profile_labeler: BotLabeler = BotLabeler()

@profile_labeler.message(payload={'cmd': 'my_profile'})
async def profile_enter_handler(message: Message):
    async with async_session_maker() as session:
        async with session.begin():
            query = select(UserModel).where(UserModel.id==482393697)
            user_info = await session.execute(query)
            print(user_info.all())
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_PROFILE)
    await message.answer(
        "Вы вошли на страницу вашего профиля",
        keyboard=back_main_menu_keyboard
    )
    profile_inline_keyboard = vk.Keyboard(inline=True)
    await message.answer(
        "Профиль",
        keyboard=vk.Keyboard(inline=True)
    )