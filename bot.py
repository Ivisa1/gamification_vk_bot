import vkbottle as vk

from globals import BOT_TOKEN

# Экземпляр бота
bot: vk.Bot = vk.Bot(BOT_TOKEN)

from handlers import labelers

# Загружаем 
for labeler in labelers:
    print('Загрузил')
    bot.labeler.load(labeler)
