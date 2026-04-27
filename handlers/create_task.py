import vkbottle as vk
from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle.dispatch.rules import OrRule, NotRule, AndRule
from vkbottle.dispatch.rules.base import PayloadRule, StateRule

from bot import bot
from states import UserStates
from keyboards import back_main_menu_keyboard

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
    # print(await bot.state_dispenser.get(peer_id=message.peer_id))
    state_peer = await bot.state_dispenser.get(message.peer_id)
    curr_state = state_peer.state if state_peer else None
    if curr_state is None or f'{curr_state}' == f'{UserStates.IN_MAIN_MENU}':
        await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_CREATE_TASK_TITLE)
        await message.answer(
            'Введите заголовок задачи: ',
            keyboard=back_main_menu_keyboard
        )
    elif 'title': ...
    elif 'desc': ...
    elif 'type': ...
    elif 'diff': ...

