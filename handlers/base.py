import asyncio
from vkbottle import GroupEventType
from vkbottle.bot import BotLabeler, Message, MessageEvent

from bot import bot, tasks_in_creation, tasks_list_params
from database import check_user_reg
from db_engine import async_session_maker
from keyboards import KeyboardCreator as KC
from logic import empty_callback_answer
from models import UserModel, UserCountersModel
from states import UserStates

base_labeler: BotLabeler = BotLabeler()

@base_labeler.message(payload={'cmd': 'main_menu'})
async def main_menu_return_handler(message: Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
    await message.answer(
        "Вы вышли в главное меню",
        keyboard=KC.main_menu_keyboard()
    )
    user_id = message.from_id
    tasks_in_creation.pop(user_id, None)

@base_labeler.message(text='/start')
async def start(message: Message):
    # Проверка на то, что пользователь уже есть в БД
    if not await check_user_reg(message.from_id):
        async with async_session_maker() as session:
            print('Регистрация пользователя')
            user_data = await bot.api.users.get(user_ids=[message.from_id])
            first_name = user_data[0].first_name
            last_name = user_data[0].last_name
            user = UserModel(
                id=message.from_id,
                first_name=first_name,
                last_name=last_name,
                current_xp=0
            )
            session.add(user)
            await session.flush()
            user_counters = UserCountersModel(
                id=message.from_id
            )
            session.add(user_counters)
            await session.commit()
            print('Пользователь зарегистрирован')

    user_id = message.from_id
    tasks_in_creation.pop(user_id, None)
    tasks_list_params.pop(user_id, None)
    await message.answer('Вы были успешно зарегестрированы. Приятного использования 😎', keyboard=KC.main_menu_keyboard())

@base_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
async def unknown_event(event: MessageEvent):
    await asyncio.sleep(0.4)
    await empty_callback_answer(event)

@base_labeler.message()
async def unknown_message(message: Message):
    user = await bot.api.users.get(user_ids=[1106823933])
    # pprint(user, indent=3, width=40)
    await message.answer(
        "Неизвестное сообщение. "
        "Напишите /start для перезапуска бота и выхода в главное меню"
    )