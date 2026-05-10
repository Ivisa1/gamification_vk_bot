from typing import Dict
import vkbottle as vk

from globals import BOT_TOKEN, SERVICE_TOKEN
from models import TasksModel, UserModel

# Экземпляр бота
bot: vk.Bot = vk.Bot(BOT_TOKEN)
service_api: vk.API = vk.API(token=SERVICE_TOKEN)

# Задачи в процессе создания
tasks_in_creation: Dict[int, UserModel] = {}

# Структура ключей
# {user_id: {'types', 'difficulties', 'tasks_count', 'curr_offset'}}
# user_id - уникальный идентификатор пользователя (одинаковый в СУБД и ВКонтакте)
# types - типы задач, которые будут выведены пользователю
# difficulties - сложности задач, которые будут выведены пользователю
# tasks_count - количество задач, соответствующих фильтрам
# curr_offset - номер текущей задачи, которая отображается пользователю
tasks_list_params: Dict[int, Dict[str, str]] = {}

from handlers import labelers

# Загружаем 
for labeler in labelers:
    bot.labeler.load(labeler)

