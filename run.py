import logging
from os import getenv

from aiogram import executor
from aiogram.types import Message

from avbot import bot, dp
from keyboards import ButtonText, Keyboards
from lang import i18n
from post import Post
from tasks import Scheduler, PeriodicTask

# noinspection PyUnresolvedReferences
import post_filters

logging.basicConfig(level=(logging.WARNING, logging.INFO, logging.DEBUG)[int(getenv('BOT_DEBUG') or 0)])

_ = __ = i18n.gettext
___ = i18n.lazy_gettext

scheduler = Scheduler(
    PeriodicTask(1, '22:00', ___('nightSpam')),
    PeriodicTask(5, '18:00', ___('daySpam')),
)


@dp.message_handler(commands=['start'])
async def h__start(msg: Message):
    await msg.answer("Hi!\nI'm Avezor bot!", reply_markup=Keyboards.country_selection)


@dp.message_handler(text=ButtonText.country_georgia)
async def h__any__country_georgia(msg: Message):
    await i18n.set_locale(msg.from_user, 'ka')
    await msg.answer('[что-то на грузинском (или и тут нужна мультиязычность?)]', reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.country_ukraine)
async def h__any__country_ukraine(msg: Message):
    await i18n.set_locale(msg.from_user, 'uk')
    await msg.answer('Вы выбрали Украину.', reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.change_country)
async def h__any__change_country(msg: Message):
    await h__start(msg)


@dp.message_handler(text=ButtonText.add_object)
async def h__add_object(msg: Message):
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
async def h__send_post(msg: Message):
    posts = [Post('229500', 'com'), Post('231004', 'ge')]
    for post in posts:
        await bot.send_photo(msg.chat.id, post.get_photo_url(),
                             post.get_description(), reply_markup=post.get_buttons())


@dp.message_handler()
async def h__any__wrong(msg: Message):
    await msg.answer(_("Something's wrong, I can feel it."))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=scheduler.get_periodic_tasks)
