from typing import Dict, List
import vkbottle as vk

from globals import BOT_TOKEN, SERVICE_TOKEN
from models import TasksModel, UserModel, TypeEnum, DifficultyEnum

# Экземпляр бота
bot: vk.Bot = vk.Bot(BOT_TOKEN)
service_api: vk.API = vk.API(token=SERVICE_TOKEN)

# Задачи в процессе создания
tasks_in_creation: Dict[int, UserModel] = {}

# Структура ключей
# {user_id: {'types', 'difficulties', 'tasks_count', 'curr_offset', 'curr_task'}}
# user_id - уникальный идентификатор пользователя (одинаковый в СУБД и ВКонтакте)
# types - типы задач, которые будут выведены пользователю
# difficulties - сложности задач, которые будут выведены пользователю
# tasks_count - количество задач, соответствующих фильтрам
# curr_offset - порядковый номер текущей задачи, которая отображается пользователю (начинается с нуля)
# curr_task - объект текущей отображаемой задачи
tasks_list_params: Dict[int, Dict[str, int | TasksModel | List[TypeEnum] | List[DifficultyEnum]]] = {}

from handlers import labelers

# Загружаем обработчики в бота
for labeler in labelers:
    bot.labeler.load(labeler)

