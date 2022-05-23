import logging
from os import getenv

from aiogram import Bot, Dispatcher, executor, types

from keyboards import Keyboards, ButtonText
from tasks import TelegramPeriodicTask, Scheduler
from text_config import *

API_TOKEN = getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

periodic_tasks = TelegramPeriodicTask(Scheduler(bot, '22:00', night_text))


@dp.message_handler(commands=['start'])
async def h__start(message: types.Message):
    await message.reply("Hi!\nI'm Avezor bot!", reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.add_object)
async def h__add__object(message: types.Message):
    await message.reply(add_object_text, reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.jobs)
async def h__jobs(message: types.Message):
    await message.reply(jobs_text, reply_markup=Keyboards.start)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=periodic_tasks.on_startup)
