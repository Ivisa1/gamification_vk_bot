import vkbottle as vk

# Клавиатуры
main_menu_keyboard = (
    vk.Keyboard(inline=False)
    .add(vk.Text('Создать задачу', payload={'cmd': 'create_task'}), color=vk.KeyboardButtonColor.PRIMARY)
    .add(vk.Text('Просмотреть задачи', payload={'cmd': 'tasks_list'}), color=vk.KeyboardButtonColor.SECONDARY)
    .row()
    .add(vk.Text('Мой профиль', payload={'cmd': 'my_profile'}), color=vk.KeyboardButtonColor.SECONDARY)
    .add(vk.Text('Таблица лидеров', payload={'cmd': 'leaderboard'}), color=vk.KeyboardButtonColor.SECONDARY)
)

choose_tasks_per_type_keyboard = (
    vk.Keyboard(inline=True)
    .add(vk.Callback('Постоянные задачи', payload={'tasks': 'reusable'}), color=vk.KeyboardButtonColor.PRIMARY)
    .row()
    .add(vk.Callback('Одноразовые задачи', payload={'tasks': 'disposable'}), color=vk.KeyboardButtonColor.PRIMARY)
)

back_main_menu_keyboard = (
    vk.Keyboard(inline=False)
    .add(vk.Text('Вернуться в главное меню', payload={'cmd': 'main_menu'}))
)
