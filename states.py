from vkbottle import BaseStateGroup

# Состояния, в которых может находиться пользователь (для навигации)
class UserStates(BaseStateGroup):
    # Состояние в главном меню
    IN_MAIN_MENU = "in_main_menu"

    # Состояния в профиле
    IN_PROFILE = "in_profile"

    # Состояния в таблице лидеров
    IN_LEADERBOARD_GLOBAL = "in_leaderboard_global"
    IN_LEADERBOARD_FRIENDS = "in_leaderboard_friends"

    # Состояния в меню созданных задач
    IN_TASKS = "in_tasks" # В общем меню задач
    IN_REUSABLE_TASKS = 'in_reusable_tasks' # В менб многоразовых задач
    IN_DISPOSABLE_TASKS = 'in_disposable_tasks' # В меню одноразовых задач

    # Состояния во время создания задачи
    IN_CREATE_TASK_TITLE = 'in_create_task_title'
    IN_CREATE_TASK_DESCRIPTION = 'in_create_task_description'
    IN_CREATE_TASK_DIFFICULCY = 'in_create_task_difficulcy'
    IN_CREATE_TASK_TYPE = 'in_create_task_type'
