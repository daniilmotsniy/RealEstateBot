import logging
from os import getenv

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message

from keyboards import ButtonText, Keyboards
from post import Post
from tasks import Scheduler, PeriodicTask
from lang import i18n

if getenv('BOT_DEBUG'):
    logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=getenv('BOT_TOKEN'))
mem = MemoryStorage()
dp = Dispatcher(bot, storage=mem)

dp.middleware.setup(i18n)

_ = __ = i18n.gettext
___ = i18n.lazy_gettext

scheduler = Scheduler(
    PeriodicTask(bot, 1, '22:00', ___('nightSpam')),
    PeriodicTask(bot, 5, '18:00', ___('daySpam')),
)


@dp.message_handler(commands=['start'])
async def h__start(msg: Message):
    await msg.answer("Hi!\nI'm Avezor bot!", reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.add_object)
async def h__add__object(msg: Message):
    await msg.answer(_('buttonReply_addObject'), reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.jobs)
async def h__jobs(msg: Message):
    await msg.answer(_('buttonReply_jobs'), reply_markup=Keyboards.start)


@dp.message_handler(commands=['lang'])
async def h__lang(msg: Message, locale: str):
    await msg.answer(_('Current language: {lang}.').format(lang=locale))

    locale = msg.get_args()

    if await i18n.set_locale(msg.from_user, locale):
        await msg.answer(_('Changed language to: {lang}.').format(lang=locale),
                         reply_markup=Keyboards.start)
    else:
        await msg.answer(_('Language {lang} not found.').format(lang=locale))


@dp.message_handler(commands=['send'])
async def h__send__post(msg: Message):
    posts = [Post('229500', 'com')]
    for post in posts:
        await bot.send_photo(msg.chat.id, post.get_photo_url(),
                             post.get_description(), reply_markup=post.get_buttons())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=scheduler.get_periodic_tasks)
