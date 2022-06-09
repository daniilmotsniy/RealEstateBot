import logging
from os import getenv

from aiogram import executor, filters
from aiogram.types import Message

from avbot import dp, mem
from keyboards import ButtonText, Keyboards
from lang import i18n
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
    await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start['ka'])


@dp.message_handler(text=ButtonText.lang_russian)
async def h__any__lang_russian(msg: Message):
    await i18n.set_locale(msg.from_user, 'ru')
    await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start['ru'])


@dp.message_handler(text=ButtonText.lang_english)
async def h__any__lang_english(msg: Message):
    await i18n.set_locale(msg.from_user, 'en')
    await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start['en'])


@dp.message_handler(text=ButtonText.country_ukraine)
async def h__any__country_ukraine(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, country='ua')
    await i18n.set_locale(msg.from_user, 'ru')
    await msg.answer('Вы выбрали Украину.', reply_markup=Keyboards.start['ru'])


@dp.message_handler(filters.Text(ButtonText.change_country.values()))
async def h__any__change_country(msg: Message):
    await h__start(msg)


@dp.message_handler(filters.Text(ButtonText.add_object.values()))
async def h__add_object(msg: Message):
    await msg.answer(_('buttonReply_addObject'))


@dp.message_handler(filters.Text(ButtonText.jobs.values()))
async def h__jobs(msg: Message):
    await msg.answer(_('buttonReply_jobs'))


@dp.message_handler()
async def h__any__wrong(msg: Message):
    await msg.answer(_("Something's wrong, I can feel it."))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=scheduler.get_periodic_tasks)
