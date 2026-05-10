from random import randint
import vkbottle as vk
from vkbottle import NotRule, OrRule, AndRule
from vkbottle.bot import BotLabeler, rules, MessageEvent, Message
from sqlalchemy import select, and_, delete, update
from typing import List

from asyncio import sleep as a_sleep
from bot import bot, tasks_list_params
from db_engine import async_session_maker
from randomiser import randomiser
from logic import empty_callback_answer, get_task, show_task, add_xp, how_much_xp, increment_counter
from models import TasksModel, UserModel, UserCountersModel, TypeEnum, DifficulcyEnum
from states import UserStates
from keyboards import KeyboardCreator as KC

tasks_list_labeler: BotLabeler = BotLabeler()

class CustomStateRule(vk.ABCRule[MessageEvent]):
    def __init__(self, state):
        self.state = state

    async def check(self, event: MessageEvent):
        curr_state = await bot.state_dispenser.get(event.object.peer_id)
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
    OrRule(
        AndRule(
            rules.PayloadContainsRule({'cmd': 'show_tasks'}),
            rules.StateRule(UserStates.IN_CHOOSE_TASKS)
        ),
        rules.PayloadContainsRule({'task': 'prev'}),
        rules.PayloadContainsRule({'task': 'next'}),
        rules.PayloadContainsRule({'task': 'complete'}),
        rules.PayloadContainsRule({'task': 'delete'})
    )
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

    await bot.state_dispenser.set(peer_id=message.peer_id, state=UserStates.IN_TASKS)
    # Удаляем сообщения предыдущего меню
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
    if tasks_list_params[user_id]['tasks_count'] == 0:
        await message.answer(
            'У вас нет задач, подходящих под заданные параметры.'
        )
        return
    task = await get_task(user_id)
    tasks_list_params[user_id]['curr_task'] = task
    str_task_info = show_task(task)
    await message.answer(
        str_task_info,
        keyboard=KC.task_keyboard(tasks_list_params[user_id], task.id)
    )

@tasks_list_labeler.raw_event(
    vk.GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    OrRule(
        rules.PayloadContainsRule({'task': 'prev'}),
        rules.PayloadContainsRule({'task': 'next'}),
        rules.PayloadContainsRule({'task': 'complete'}),
        rules.PayloadContainsRule({'task': 'delete'})
    ),
    CustomStateRule(UserStates.IN_TASKS)
)
async def edit_show_tasks(event: MessageEvent):
    await a_sleep(0.4)
    user_id = event.user_id
    action = event.get_payload_json().pop('task')
    match action:
        case 'prev':
            if tasks_list_params[user_id]['curr_offset'] > 0:
                tasks_list_params[user_id]['curr_offset'] -= 1
        case 'next':
            if tasks_list_params[user_id]['curr_offset'] < tasks_list_params[user_id]['tasks_count']:
                tasks_list_params[user_id]['curr_offset'] += 1
        case 'complete':
            await complete_task(tasks_list_params[user_id]['curr_task'])
            if tasks_list_params[user_id]['curr_task'].type == TypeEnum.DISPOSABLE:
                if tasks_list_params[user_id]['curr_offset'] != 0:
                    tasks_list_params[user_id]['curr_offset'] -= 1
                tasks_list_params[user_id]['tasks_count'] -= 1
        case 'delete':
            await delete_task(tasks_list_params[user_id]['curr_task'])
            tasks_list_params[user_id]['tasks_count'] -= 1
            if tasks_list_params[user_id]['curr_offset'] != 0:
                tasks_list_params[user_id]['curr_offset'] -= 1
        case _:
            pass
    if tasks_list_params[user_id]['tasks_count'] == 0:
        await bot.api.messages.edit(
            peer_id=event.peer_id,
            cmid=event.conversation_message_id,
            message='У вас нет задач, подходящих под заданные параметры.',
            keyboard=vk.Keyboard(inline=True)
        )
        return
    task = await get_task(user_id)
    tasks_list_params[user_id]['curr_task'] = task
    str_task_info = show_task(task)
    await bot.api.messages.edit(
        peer_id=event.peer_id,
        cmid=event.conversation_message_id,
        message=str_task_info,
        keyboard=KC.task_keyboard(tasks_list_params[user_id], task.id),
        format_data=str_task_info.as_raw_data()
    )
    await empty_callback_answer(event)

async def delete_task(task):
    async with async_session_maker() as session:
        stmt = delete(TasksModel).filter_by(id=task.id)
        await session.execute(stmt)
        await session.commit()

async def complete_task(task: TasksModel):
    async with async_session_maker() as session:
        amount = how_much_xp(task.difficulcy)
        # Добавляем пользователю опыт
        stmt = (
            update(UserModel)
            .where(UserModel.id==task.user_id)
            .values(current_xp=UserModel.current_xp+amount)
        )
        await session.execute(stmt)
        user_counters = await session.get(UserCountersModel, task.user_id)
        increment_counter(task, user_counters)
        print(user_counters.medium)
        if task.type == TypeEnum.DISPOSABLE:
            stmt = delete(TasksModel).filter_by(id=task.id)
            await session.execute(stmt)
        elif task.type == TypeEnum.REUSABLE:
            pass
        await session.commit()
