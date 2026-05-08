import vkbottle as vk

from globals import BOT_TOKEN, SERVICE_TOKEN

# Экземпляр бота
bot: vk.Bot = vk.Bot(BOT_TOKEN)
service_api: vk.API = vk.API(token=SERVICE_TOKEN)

from handlers import labelers

# Загружаем 
for labeler in labelers:
    print('Загрузил')
    bot.labeler.load(labeler)

