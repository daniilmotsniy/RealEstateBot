import logging
from os import getenv

from aiogram import executor
from aiogram.types import Message

from avbot import bot, dp, mem
from keyboards import ButtonText, Keyboards
from lang import i18n
from post import PostsFiltration
from tasks import Scheduler, PeriodicDailyText, PeriodicPostSpammer

# noinspection PyUnresolvedReferences
import post_filters

logging.basicConfig(level=(logging.WARNING, logging.INFO, logging.DEBUG)[int(getenv('BOT_DEBUG') or 0)])

_ = __ = i18n.gettext
___ = i18n.lazy_gettext

scheduler = Scheduler(
    PeriodicDailyText(1, '22:00', ___('nightSpam')),
    PeriodicDailyText(5, '18:00', ___('daySpam')),
    PeriodicPostSpammer(10),
)


@dp.message_handler(commands=['start'])
async def h__start(msg: Message):
    await msg.answer("Hi!\nI'm Avezor bot!", reply_markup=Keyboards.country_selection)


@dp.message_handler(text=ButtonText.country_georgia)
async def h__any__country_georgia(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, country='ge')
    await msg.answer(_("Выберите язык"), reply_markup=Keyboards.ge_lang_selection)


@dp.message_handler(text=ButtonText.lang_georgian)
async def h__any__lang_georgian(msg: Message):
    await i18n.set_locale(msg.from_user, 'ka')
    await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.lang_russian)
async def h__any__lang_russian(msg: Message):
    await i18n.set_locale(msg.from_user, 'ru')
    await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start)


@dp.message_handler(text=ButtonText.country_ukraine)
async def h__any__country_ukraine(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, country='ua')
    await i18n.set_locale(msg.from_user, 'ru')
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


@dp.message_handler(commands=['send'])
async def h__send_post(msg: Message):
    posts = await PostsFiltration(msg.from_user.id).find_estate()
    posts_len = len(posts)
    found_text = f'I have found {posts_len} posts!'
    if posts_len > 0:
        found_text += ' '
        found_text += 'Wait, I am sending ...'
    await bot.send_message(msg.chat.id, found_text)
    for post in posts:
        await bot.send_photo(msg.chat.id, post.get_photo_url(),
                             post.get_description(), reply_markup=post.get_buttons())


@dp.message_handler()
async def h__any__wrong(msg: Message):
    await msg.answer(_("Something's wrong, I can feel it."))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=scheduler.get_periodic_tasks)
