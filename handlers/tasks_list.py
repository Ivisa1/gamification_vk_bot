from random import randint
import vkbottle as vk
from vkbottle import NotRule, OrRule
from vkbottle.bot import BotLabeler, rules, MessageEvent, Message
from sqlalchemy import select, and_
from typing import List

from bot import bot, tasks_list_params
from db_engine import async_session_maker
from randomiser import randomiser
from logic import empty_callback_answer, get_task
from models import TasksModel, TypeEnum, DifficulcyEnum
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
@tasks_list_labeler.message(
    rules.PayloadContainsRule({'cmd': 'tasks_filters'})
)
async def tasks_list_enter_handler(message: Message):
    params = message.get_payload_json().get('params', {})
    if not params:
        params['types'] = {'reusable': True, 'disposable': True}
        params['difficulties'] = {'very_easy': True, 'easy': True, 'medium': True, 'hard': True, 'very_hard': True}
    print(tasks_list_params)
    tasks_list_params.pop(message.from_id, None)
    print(tasks_list_params)
    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_CHOOSE_TASKS)
    await message.answer('Вы вошли на страницу ваших задач', keyboard=KC.back_main_menu_keyboard())
    await message.answer(
        "Выберите, какие задачи хотите просмотреть (Оч. Лёгк. - очень лёгкие, Лёгк. - лёгкие, Средн. - средние, "
        "Сложн. - сложные, Оч. Сложн.:",
        keyboard=KC.choose_tasks_keyboard(params['types'], params['difficulties'])
    )

@tasks_list_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    CustomStateRule(UserStates.IN_CHOOSE_TASKS),
    NotRule(rules.PayloadRule({'cmd': 'main_menu'}))
)
async def change_tasks_panel(event: MessageEvent):
    await empty_callback_answer(event)
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
    payload_contains={'cmd': 'show_tasks'},
    state=UserStates.IN_CHOOSE_TASKS
)
async def show_tasks(message: Message):
    user_id = message.from_id
    # Если пользователь только что открыл список своих задач
    if not tasks_list_params.get(user_id, {}):
        tasks_list_params[user_id] = {}
        payload_params = message.get_payload_json()['params']
        types_list: List[TypeEnum] = []
        for type_ in payload_params['types']:
            if payload_params['types'][type_]:
                types_list.append(TypeEnum(type_))
        print(types_list)
        tasks_list_params[user_id]['types'] = types_list
        difficulties_list: List[DifficulcyEnum] = []
        for difficulty_ in payload_params['difficulties']:
            if payload_params['difficulties'][difficulty_]:
                difficulties_list.append(DifficulcyEnum(difficulty_))
        print(difficulties_list)
        tasks_list_params[user_id]['difficulties'] = difficulties_list
        # Подсчет количества задач, подходящих под заданные критерии
        async with async_session_maker() as session:
            stmt = (
                select(TasksModel)
                .where(and_(TasksModel.user_id==user_id, TasksModel.type.in_(types_list), TasksModel.difficulcy.in_(difficulties_list)))
            )
            result = await session.execute(stmt)
            tasks = result.all()
            print(tasks)
            tasks_list_params[user_id]['tasks_count'] = len(tasks)
        tasks_list_params[user_id]['curr_offset'] = 0
        print(tasks_list_params)

    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_TASKS)
    filters_message: Message = await bot.api.messages.search(
        q='Выберите, ',
        peer_id=message.peer_id,
        count=1
    )
    messages_to_delete = filters_message.items
    filters_message: Message = await bot.api.messages.search(
        q='Вы вошли ',
        peer_id=message.peer_id,
        count=1
    )
    messages_to_delete.append(filters_message.items[0])
    try:
        await bot.api.messages.delete(
            message_ids=[messages_to_delete[0].id, messages_to_delete[1].id],
            delete_for_all=1
        )
    except Exception as e:
        print(f'Не удалось удалить сообщение: {e}')
    await message.answer(
        'Ваш список задач, соответствующий заданным фильтрам:',
        keyboard=KC.back_to_choose_tasks_keyboard(message.get_payload_json()['params'])
    )
    # await message.answer(
    #     'Вывод задачи',
    #     keyboard=KC.task_keyboard()
    # )