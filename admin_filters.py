from aiogram import filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram.types import Message, User, ReplyKeyboardMarkup

from admin import SpamToUsers
from avbot import dp, mem
from keyboards import ButtonText, Keyboards

from lang import i18n

_ = __ = i18n.gettext


class Form(StatesGroup):
    message = State()
    agree = State()


@dp.message_handler(filters.Text(ButtonText.send_to_users.values()))
async def h__any__send_to_users(msg: Message):
    await Form.message.set()
    await msg.reply("Write a message, please.")


@dp.message_handler(state=Form.message)
async def q__type__to_users(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['message_to_users'] = message.text
        await Form.next()
        await state.update_data(message=data['message_to_users'])
        markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

        markup.add("Yes", "No")

        await message.reply("Send a message?", reply_markup=markup)


@dp.message_handler(state=Form.agree)
async def process_gender(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['agree'] = message.text
        await state.update_data(agree=data['agree'])
        bucket = await mem.get_bucket(user=User.get_current().id)
        locale = bucket['locale']
        is_admin = 'is_admin' in bucket.keys() and bucket['is_admin']
        if data['agree'] == 'Yes' and is_admin:
            country = bucket['country']
            await SpamToUsers(country, locale, data['message_to_users']).spam()
            await message.answer('Message was sent!', reply_markup=Keyboards.start_admin[locale])
        elif data['agree'] == 'No':
            await message.answer('You have declined message ;(', reply_markup=Keyboards.start_admin[locale])
        else:
            await message.answer('You have no permissions for that!', reply_markup=Keyboards.start_admin[locale])
        await state.finish()
