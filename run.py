import logging
from os import getenv

from aiogram import executor, filters
from aiogram.types import Message

from avbot import dp, mem
from keyboards import ButtonText, Keyboards
from lang import i18n
from tasks import Scheduler, PeriodicPostSpammer

# noinspection PyUnresolvedReferences
import post_filters

# noinspection PyUnresolvedReferences
import admin_filters

logging.basicConfig(level=(logging.WARNING, logging.INFO, logging.DEBUG)[int(getenv('BOT_DEBUG') or 0)])

_ = __ = i18n.gettext

night_spam = """
Сейчас уже поздно и для Вашего комфорта я буду отправлять варианты без звука. Доброй ночи! 😴 

ახლა უკვე გვიანია , ამიტომ თქვენი კომფორტისთვის ყველა ახალ ვარიანტს გამოგიგზავნით დილით.ღამემშვიდობის.😴
 
It's late now and for your comfort I'll send all the new options in the morning. Good night! 😴
"""

day_spam = """
Нет подходящих вариантов? Попробуйте изменить критерии поиска.

არ არის შესაფერისი ვარიანტები? სცადეთ შეცვალოთ თქვენი ძიების კრიტერიუმები.

No suitable options? Try changing your search criteria.
"""

scheduler = Scheduler(
    # PeriodicDailyText(1, '22:00', night_spam),
    # PeriodicDailyText(5, '14:00', day_spam),
    PeriodicPostSpammer(1),
)


@dp.message_handler(commands=['start'])
async def h__start(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, country='ge')
    await msg.answer(f"🐼 Hi {msg.from_user.first_name}!\nI'm Avezor bot!\nPlease select a language.", reply_markup=Keyboards.ge_lang_selection)
    await mem.update_bucket(user=msg.from_user.id, username=msg.from_user.username)


@dp.message_handler(text=ButtonText.country_georgia)
async def h__any__country_georgia(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, country='ge')
    await msg.answer(_("Выберите язык"), reply_markup=Keyboards.ge_lang_selection)


@dp.message_handler(text=ButtonText.lang_georgian)
async def h__any__lang_georgian(msg: Message):
    await i18n.set_locale(msg.from_user, 'ka')

    bucket = await mem.get_bucket(user=msg.from_user.id)

    if 'is_admin' not in bucket.keys() or not bucket['is_admin']:
        await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start['ka'])
    else:
        await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start_admin['ka'])


@dp.message_handler(text=ButtonText.lang_russian)
async def h__any__lang_russian(msg: Message):
    await i18n.set_locale(msg.from_user, 'ru')

    bucket = await mem.get_bucket(user=msg.from_user.id)

    if 'is_admin' not in bucket.keys() or not bucket['is_admin']:
        await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start['ru'])
    else:
        await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start_admin['ru'])


@dp.message_handler(text=ButtonText.lang_english)
async def h__any__lang_english(msg: Message):
    await i18n.set_locale(msg.from_user, 'en')

    bucket = await mem.get_bucket(user=msg.from_user.id)

    if 'is_admin' not in bucket.keys() or not bucket['is_admin']:
        await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start['en'])
    else:
        await msg.answer(_("Язык выбран"), reply_markup=Keyboards.start_admin['en'])


@dp.message_handler(text=ButtonText.country_ukraine)
async def h__any__country_ukraine(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, country='ua')
    await i18n.set_locale(msg.from_user, 'ru')
    bucket = await mem.get_bucket(user=msg.from_user.id)

    if 'is_admin' not in bucket.keys() or not bucket['is_admin']:
        await msg.answer('Вы выбрали Украину 🇺🇦', reply_markup=Keyboards.start['ru'])
    else:
        await msg.answer('Вы выбрали Украину 🇺🇦', reply_markup=Keyboards.start_admin['ru'])


@dp.message_handler(filters.Text(ButtonText.change_country.values()))
async def h__any__change_country(msg: Message):
    await h__start(msg)


@dp.message_handler(filters.Text(ButtonText.change_language.values()))
async def h__any__change_country(msg: Message):
    await h__start(msg)


@dp.message_handler(filters.Text(ButtonText.add_object.values()))
async def h__add_object(msg: Message):
    await msg.answer(_('{name} buttonReply_addObject').format(name=msg.from_user.first_name))


@dp.message_handler(filters.Text(ButtonText.jobs.values()))
async def h__jobs(msg: Message):
    await msg.answer(_('buttonReply_jobs'))


@dp.message_handler()
async def h__any__wrong(msg: Message):
    await msg.answer(_("Something's wrong, I can feel it."))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,
                           on_startup=scheduler.get_periodic_tasks)
