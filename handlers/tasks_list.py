from random import randint
import vkbottle as vk
from vkbottle import NotRule
from vkbottle.bot import BotLabeler, rules, MessageEvent, Message
from sqlalchemy import select, and_

from bot import bot
from db_engine import async_session_maker
from randomiser import randomiser
from logic import empty_callback_answer, get_task
from models import TasksModel, TypeEnum
from states import UserStates
from keyboards import KeyboardCreator as KC

tasks_list_labeler: BotLabeler = BotLabeler()

class CustomStateRule(vk.ABCRule[MessageEvent]):
    def __init__(self, state):
        self.state = state

    async def check(self, event: MessageEvent):
        curr_state = await bot.state_dispenser.get(event.object.peer_id)
        print(f"Проверка состояния: текущее={curr_state.state}, ожидаемое={self.state}")  # Отладка
        return curr_state.state == self.state

tasks_list_labeler.custom_rules['custom_state'] = CustomStateRule

# Переход в раздел с созданными задачами
@tasks_list_labeler.message(payload={'cmd': 'tasks_list'})
async def tasks_list_enter_handler(message: Message):
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_TASKS)
    await message.answer('Вы вошли на страницу ваших задач', keyboard=KC.back_main_menu_keyboard())
    await message.answer(
        "Выберите, какие задачи хотите просмотреть (Оч. Лёгк. - очень лёгкие, Лёгк. - лёгкие, Средн. - средние, "
        "Сложн. - сложные, Оч. Сложн.:",
        keyboard=KC.choose_tasks_keyboard()
    )

@tasks_list_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    rules.PayloadRule({'tasks': 'reusable'}),
    custom_state=UserStates.IN_TASKS
)
async def reusable_tasks_enter_handler(event: MessageEvent):
    await bot.state_dispenser.set(peer_id=event.object.peer_id, state=UserStates.IN_REUSABLE_TASKS)
    await empty_callback_answer()
    await bot.api.messages.send(
        user_id=event.object.user_id,
        random_id=randomiser.randint(0, 10000),
        peer_id=event.object.peer_id,
        message='Ваши постоянные задачи',
        keyboard=KC.back_main_menu_keyboard()
    )
    # Нужно создать клавиатуру для управления задачами и добавить её в запрос ниже
    curr_offset = 0
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
async def disposable_tasks_enter_handler(event: MessageEvent):
    await bot.state_dispenser.set(peer_id=event.object.peer_id, state=UserStates.IN_DISPOSABLE_TASKS)
    await empty_callback_answer()
    await bot.api.messages.send(
        user_id=event.object.user_id,
        random_id=randomiser.randint,
        peer_id=event.object.peer_id,
        message='Ваши одноразовые задачи',
        keyboard=KC.back_main_menu_keyboard()
    )
    # Нужно создать клавиатуру для управления задачами и добавить её в запрос ниже
    await bot.api.messages.send(
        user_id=event.object.user_id,
        random_id=randomiser.randint,
        peer_id=event.object.peer_id,
        message='Задача', # Тут выводить задачи из БД
        keyboard=None
    )

@tasks_list_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    CustomStateRule(UserStates.IN_TASKS),
    NotRule(rules.PayloadRule({'cmd': 'main_menu'}))
)
async def change_tasks_panel(event: MessageEvent):
    await empty_callback_answer()
    await bot.api.messages.edit(
        peer_id=event.peer_id,
        cmid=event.object.conversation_message_id,
        message=(
            "Выберите, какие задачи хотите просмотреть (Оч. Лёгк. - очень лёгкие, Лёгк. - лёгкие, Средн. - средние, "
            "Сложн. - сложные, Оч. Сложн.:"
        ),
        keyboard=KC.choose_tasks_keyboard(
            types=event.payload['types'],
            difficulties=event.payload['difficulties']
        )
    )

@tasks_list_labeler.message(
    payload_contains={'tasks': 'show'},
    state=UserStates.IN_TASKS
)
async def show_tasks(message: Message):
    await message.answer(
        'Вывод задач',
        keyboard=KC.task_keyboard
    )