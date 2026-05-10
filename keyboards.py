import vkbottle as vk
from vkbottle import KeyboardButtonColor as color
from typing import Dict

# Клавиатуры
main_menu_keyboard = (
    vk.Keyboard(inline=False)
    .add(vk.Text('Создать задачу', payload={'cmd': 'create_task'}), color=color.PRIMARY)
    .add(vk.Text('Просмотреть задачи', payload={'cmd': 'tasks_list'}), color=color.SECONDARY)
    .row()
    .add(vk.Text('Мой профиль', payload={'cmd': 'my_profile'}), color=color.SECONDARY)
    .add(vk.Text('Таблица лидеров', payload={'cmd': 'leaderboard'}), color=color.SECONDARY)
)

choose_tasks_per_type_keyboard = (
    vk.Keyboard(inline=True)
    .add(vk.Callback('Постоянные задачи', payload={'tasks': 'reusable'}), color=color.PRIMARY)
    .row()
    .add(vk.Callback('Одноразовые задачи', payload={'tasks': 'disposable'}), color=color.PRIMARY)
)

back_main_menu_keyboard = (
    vk.Keyboard(inline=False)
    .add(vk.Text('Вернуться в главное меню', payload={'cmd': 'main_menu'}))
)

class KeyboardCreator():

    def main_menu_keyboard():
        return (
            vk.Keyboard(inline=False)
            .add(vk.Text('Создать задачу', payload={'cmd': 'create_task'}), color=color.PRIMARY)
            .add(vk.Text('Просмотреть задачи', payload={'cmd': 'tasks_filters'}), color=color.SECONDARY)
            .row()
            .add(vk.Text('Мой профиль', payload={'cmd': 'my_profile'}), color=color.SECONDARY)
            .add(vk.Text('Таблица лидеров', payload={'cmd': 'leaderboard'}), color=color.SECONDARY)
        )
    
    def back_main_menu_keyboard():
        return (
            vk.Keyboard(inline=False)
            .add(vk.Text('Вернуться в главное меню', payload={'cmd': 'main_menu'}))
        )
    
    def choose_tasks_keyboard(
        types: Dict[str, bool]={'reusable': True, 'disposable': True},
        difficulties: Dict[str, bool]={'very_easy': True, 'easy': True, 'medium': True, 'hard': True, 'very_hard': True}
    ):
        return (
            vk.Keyboard(inline=True)
            .add(
                vk.Callback(
                    ('* ' if types['reusable'] else '') + 'Постоянные',
                    payload=payload_for_choose_tasks_keyboard(types.copy(), difficulties.copy(), 'types', 'reusable')
                ),
                color=color.PRIMARY if types['reusable'] else color.SECONDARY
            )
            .add(
                vk.Callback(
                    ('* ' if types['disposable'] else '') + 'Одноразовые', 
                    payload=payload_for_choose_tasks_keyboard(types.copy(), difficulties.copy(), 'types', 'disposable')
                ), 
                color=color.PRIMARY if types['disposable'] else color.SECONDARY
            )
            .row()
            .add(
                vk.Callback(
                    ('* ' if difficulties['very_easy'] else '') + 'Оч. Лёгк.', 
                    payload=payload_for_choose_tasks_keyboard(types.copy(), difficulties.copy(), 'difficulties', 'very_easy')
                ), 
                color=color.PRIMARY if difficulties['very_easy'] else color.SECONDARY
            )
            .add(
                vk.Callback(
                    ('* ' if difficulties['easy'] else '') + 'Лёгк.', 
                    payload=payload_for_choose_tasks_keyboard(types.copy(), difficulties.copy(), 'difficulties', 'easy')
                ), 
                color=color.PRIMARY if difficulties['easy'] else color.SECONDARY
            )
            .add(
                vk.Callback(
                    ('* ' if difficulties['medium'] else '') + 'Средн.', 
                    payload=payload_for_choose_tasks_keyboard(types.copy(), difficulties.copy(), 'difficulties', 'medium')
                ), 
                color=color.PRIMARY if difficulties['medium'] else color.SECONDARY
            )
            .row()
            .add(
                vk.Callback(
                    ('* ' if difficulties['hard'] else '') + 'Сложн.', 
                    payload=payload_for_choose_tasks_keyboard(types.copy(), difficulties.copy(), 'difficulties', 'hard')
                ), 
                color=color.PRIMARY if difficulties['hard'] else color.SECONDARY
            )
            .add(
                vk.Callback(
                    ('* ' if difficulties['very_hard'] else '') + 'Оч. Сложн.', 
                    payload=payload_for_choose_tasks_keyboard(types.copy(), difficulties.copy(), 'difficulties', 'very_hard')
                ), 
                color=color.PRIMARY if difficulties['very_hard'] else color.SECONDARY
            )
            .row()
            .add(
                vk.Text(
                    'Показать задачи',
                    payload=payload_for_choose_tasks_keyboard(types, difficulties)
                ),
                color=color.POSITIVE
            )
        )
    
    def in_leaderboard_keyboard(type='global'):
        return (
            vk.Keyboard(inline=True)
            .add(vk.Callback(
                ('* ' if type=='friends' else '') + 'Друзья',
                payload={'leaderboard': 'friends'}),
                color=color.PRIMARY if type=='friends' else color.SECONDARY
            )
            .add(vk.Callback(
                ('* ' if type=='global' else '') + 'Глобально',
                payload={'leaderboard': 'global'}),
                color=color.PRIMARY if type=='global' else color.SECONDARY
            )
        )
    
    def task_keyboard(user_info, task_id):
        keyboard = vk.Keyboard(inline=True)
        if user_info['curr_offset']:
            keyboard.add(vk.Callback('<', payload={'task': 'prev'}), color=color.PRIMARY)
        if user_info['curr_offset']+1 < user_info['tasks_count']:
            keyboard.add(vk.Callback('>', payload={'task': 'next'}), color=color.PRIMARY)
        keyboard.row()
        # Дописать кнопки для управления задачами
        keyboard.add(vk.Callback('Выполнить задачу', payload={'task': 'complete'}), color=color.POSITIVE)
        keyboard.add(vk.Callback('Удалить задачу', payload={'task': 'delete'}), color=color.NEGATIVE)
        return keyboard

    def back_to_choose_tasks_keyboard(params):
        return (
            vk.Keyboard(inline=False)
            .add(vk.Text('Вернуться к выбору задач', payload={'cmd': 'tasks_filters', 'params': params}))
        )

def payload_for_choose_tasks_keyboard(types: Dict[str, bool], difficulties: Dict[str, bool], level_1: str = None, level_2: str = None):
    """
    Возвращает payload для кнопок из раздела фильтрации необходимых для вывода задач

    :level_1 - содержит строку-ключ для первого уровня payload-словаря\n
    :level_2 - содержит строку-ключ для второго уровня payload-словаря
    """

    payload = {'types': types, 'difficulties': difficulties}
    if level_1 is None or level_2 is None:
        return {'cmd': 'show_tasks', 'params': payload}
    payload[level_1][level_2] = not payload[level_1][level_2]
    return payload