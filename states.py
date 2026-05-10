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
    IN_CHOOSE_TASKS = "in_choose_tasks"
    IN_TASKS = "in_tasks" # В общем меню задач

    # Состояния во время создания задачи
    IN_CREATE_TASK_TITLE = 'in_create_task_title'
    IN_CREATE_TASK_DESCRIPTION = 'in_create_task_description'
    IN_CREATE_TASK_DIFFICULCY = 'in_create_task_difficulcy'
    IN_CREATE_TASK_TYPE = 'in_create_task_type'
