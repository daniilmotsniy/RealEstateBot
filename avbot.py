from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.mongo import MongoStorage

from lang import i18n

bot = Bot(token=getenv('BOT_TOKEN'))
mem = MongoStorage(db_name='AvezorBot', uri=getenv('MONGODB_URL') or 'localhost')
dp = Dispatcher(bot, storage=mem)

dp.middleware.setup(i18n)
