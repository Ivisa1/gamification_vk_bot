import vkbottle as vk
from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle.dispatch.rules import OrRule, NotRule, AndRule
from vkbottle.dispatch.rules.base import PayloadRule, StateRule

from bot import bot, tasks_in_creation
from db_engine import async_session_maker
from states import UserStates
from keyboards import KeyboardCreator as KC
from models import TasksModel, TypeEnum, DifficulcyEnum

create_task_labeler: BotLabeler = BotLabeler()

@create_task_labeler.message(
    OrRule(
        PayloadRule({'cmd': 'create_task'}),
        StateRule(
            [
                UserStates.IN_CREATE_TASK_TITLE,
                UserStates.IN_CREATE_TASK_DESCRIPTION,
                UserStates.IN_CREATE_TASK_TYPE,
                UserStates.IN_CREATE_TASK_DIFFICULCY
            ]
        )
    ),
    NotRule(PayloadRule({'cmd': 'main_menu'}))
)
async def create_task_handler(message: Message):
    state_peer = await bot.state_dispenser.get(message.peer_id)
    curr_state = state_peer.state if state_peer else None
    if curr_state is None or f'{curr_state}' == f'{UserStates.IN_MAIN_MENU}':
        await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_CREATE_TASK_TITLE)
        tasks_in_creation[message.from_id] = TasksModel(user_id=message.from_id)
        print(tasks_in_creation[message.from_id], tasks_in_creation[message.from_id].id, tasks_in_creation[message.from_id].title)
        await message.answer(
            'Введите заголовок задачи: ',
            keyboard=KC.back_main_menu_keyboard()
        )
    elif f'{curr_state}' == f'{UserStates.IN_CREATE_TASK_TITLE}':
        await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_CREATE_TASK_DESCRIPTION)
        tasks_in_creation[message.from_id].title = message.text
        await message.answer(
            'Введите описание задачи (введите ".", чтобы оставить поле пустым): '
        )
        print(tasks_in_creation)
    elif f'{curr_state}' == f'{UserStates.IN_CREATE_TASK_DESCRIPTION}':
        await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_CREATE_TASK_TYPE)
        if message.text != '.':
            tasks_in_creation[message.from_id].description = message.text
        await message.answer(
            'Введите тип задачи (1 - одноразовая, 2 - повторяющаяся): '
        )
    elif f'{curr_state}' == f'{UserStates.IN_CREATE_TASK_TYPE}':
        if message.text not in ('1', '2'):
            await message.answer(
                "Неверно введён тип задачи. Попробуйте еще раз."
            )
            return
        elif message.text == '1':
            tasks_in_creation[message.from_id].type = TypeEnum.DISPOSABLE
            await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_CREATE_TASK_DIFFICULCY)
        elif message.text == '2':
            tasks_in_creation[message.from_id].type = TypeEnum.REUSABLE
            await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_CREATE_TASK_DIFFICULCY)
        await message.answer(
            'Введите сложность задачи (1 - очень легко, 2 - легко, 3 - средне, 4 - сложно, 5 - очень сложно):'
        )
    elif f'{curr_state}' == f'{UserStates.IN_CREATE_TASK_DIFFICULCY}':
        match message.text:
            case '1':
                tasks_in_creation[message.from_id].difficulcy = DifficulcyEnum.VERY_EASY
                await add_task_in_db(message, message.from_id)
                await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
            case '2':
                tasks_in_creation[message.from_id].difficulcy = DifficulcyEnum.EASY
                await add_task_in_db(message, message.from_id)
                await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
            case '3':
                tasks_in_creation[message.from_id].difficulcy = DifficulcyEnum.MEDIUM
                await add_task_in_db(message, message.from_id)
                await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
            case '4':
                tasks_in_creation[message.from_id].difficulcy = DifficulcyEnum.HARD
                await add_task_in_db(message, message.from_id)
                await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
            case '5':
                tasks_in_creation[message.from_id].difficulcy = DifficulcyEnum.VERY_HARD
                await add_task_in_db(message, message.from_id)
                await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_MAIN_MENU)
            case _:
                await message.answer(
                    "Неверно введена сложность задачи. Попробуйте еще раз."
                )

async def add_task_in_db(message: Message, user_id: int):
    async with async_session_maker() as session:
        session.add(tasks_in_creation[user_id])
        await session.commit()
    await message.answer(
        "Задача успешно создана",
        keyboard=KC.main_menu_keyboard()
    )
