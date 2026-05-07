from random import randint
import vkbottle as vk
from vkbottle.bot import BotLabeler, rules, MessageEvent

from bot import bot
from randomiser import randomiser
from states import UserStates
from keyboards import back_main_menu_keyboard, choose_tasks_per_type_keyboard

tasks_list_labeler: BotLabeler = BotLabeler()

class CustomStateRule(vk.ABCRule[vk.bot.MessageEvent]):
    def __init__(self, state):
        self.state = state

    async def check(self, event: vk.bot.MessageEvent):
        curr_state = await bot.state_dispenser.get(event.object.peer_id)
        print(f"Проверка состояния: текущее={curr_state.state}, ожидаемое={self.state}")  # Отладка
        return curr_state.state == self.state

tasks_list_labeler.custom_rules['custom_state'] = CustomStateRule

# Переход в раздел с созданными задачами
@tasks_list_labeler.message(payload={'cmd': 'tasks_list'}, state=UserStates.IN_MAIN_MENU)
async def tasks_list_enter_handler(message: vk.Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_TASKS)
    await message.answer('Вы вошли на страницу ваших задач', keyboard=back_main_menu_keyboard)
    await message.answer(
        "Выберите, какой тип задач хотите просмотреть:",
        keyboard=choose_tasks_per_type_keyboard
    )

@tasks_list_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({'tasks': 'reusable'}),
    custom_state=UserStates.IN_TASKS
)
async def reusable_tasks_enter_handler(event: MessageEvent):
    await bot.state_dispenser.set(peer_id=event.object.peer_id, state=UserStates.IN_REUSABLE_TASKS)
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        peer_id=event.object.peer_id,
        user_id=event.object.user_id,
        event_data=None
    )
    await bot.api.messages.send(
        user_id=event.object.user_id,
        random_id=randomiser.randint(0, 10000),
        peer_id=event.object.peer_id,
        message='Ваши постоянные задачи',
        keyboard=back_main_menu_keyboard
    )
    # Нужно создать клавиатуру для управления задачами и добавить её в запрос ниже
    await bot.api.messages.send(
        user_id=event.object.user_id,
        random_id=randomiser.randint(0, 10000),
        peer_id=event.object.peer_id,
        message='Задача', # Тут выводить задачи из БД
        keyboard=None
    )

@tasks_list_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({'tasks': 'diposable'}),
    custom_state=UserStates.IN_TASKS
)
async def reusable_tasks_enter_handler(event: MessageEvent):
    await bot.state_dispenser.set(peer_id=event.object.peer_id, state=UserStates.IN_DISPOSABLE_TASKS)
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        peer_id=event.object.peer_id,
        user_id=event.object.user_id,
        event_data=None
    )
    await bot.api.messages.send(
        user_id=event.object.user_id,
        random_id=randomiser.randint,
        peer_id=event.object.peer_id,
        message='Ваши одноразовые задачи',
        keyboard=back_main_menu_keyboard
    )
    # Нужно создать клавиатуру для управления задачами и добавить её в запрос ниже
    await bot.api.messages.send(
        user_id=event.object.user_id,
        random_id=randomiser.randint,
        peer_id=event.object.peer_id,
        message='Задача', # Тут выводить задачи из БД
        keyboard=None
    )
