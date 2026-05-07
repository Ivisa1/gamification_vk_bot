import vkbottle as vk
from vkbottle import KeyboardButtonColor as color

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
            .add(vk.Text('Просмотреть задачи', payload={'cmd': 'tasks_list'}), color=color.SECONDARY)
            .row()
            .add(vk.Text('Мой профиль', payload={'cmd': 'my_profile'}), color=color.SECONDARY)
            .add(vk.Text('Таблица лидеров', payload={'cmd': 'leaderboard'}), color=color.SECONDARY)
        )
    
    def back_main_menu_keyboard():
        return (
            vk.Keyboard(inline=False)
            .add(vk.Text('Вернуться в главное меню', payload={'cmd': 'main_menu'}))
        )
    
    def choose_tasks_per_type_keyboard():
        return (
            vk.Keyboard(inline=True)
            .add(vk.Callback('Постоянные задачи', payload={'tasks': 'reusable'}), color=color.PRIMARY)
            .row()
            .add(vk.Callback('Одноразовые задачи', payload={'tasks': 'disposable'}), color=color.PRIMARY)
        )
    
    def in_leaderboard_keyboard(type='friends'):
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