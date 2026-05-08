from typing import Dict
import vkbottle as vk

from globals import BOT_TOKEN, SERVICE_TOKEN
from models import TasksModel

# Экземпляр бота
bot: vk.Bot = vk.Bot(BOT_TOKEN)
service_api: vk.API = vk.API(token=SERVICE_TOKEN)

# Задачи в процессе создания
tasks_in_creation: Dict[int, Dict[str, str]] = {}

from handlers import labelers

# Загружаем 
for labeler in labelers:
    print('Загрузил')
    bot.labeler.load(labeler)

