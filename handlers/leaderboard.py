import vkbottle as vk
from vkbottle.bot import BotLabeler

from bot import bot
from states import UserStates
from keyboards import back_main_menu_keyboard

leaderboard_labeler: BotLabeler = BotLabeler()

# Переход на страницу таблицы лидеров
@leaderboard_labeler.message(payload={'cmd': 'leaderboard'})
async def leaderboard_enter_handler(message: vk.Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_LEADERBOARD)
    await message.answer(
        "Вы вошли на страницу таблицы лидеров",
        keyboard=back_main_menu_keyboard
    )