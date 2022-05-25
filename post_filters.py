import itertools
from typing import Iterable, Union

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import wp_api
from avbot import dp
from keyboards import ButtonText
from lang import i18n

_ = __ = i18n.gettext


def create_dynamic_inline_keyboard(values: Iterable[tuple[str, Union[str, int]]], cols: int, domain: str):
    return InlineKeyboardMarkup(cols, list(itertools.zip_longest(
        *itertools.repeat((InlineKeyboardButton(str(text), callback_data=f'{domain}/{slug}') for slug, text in values), cols),
        fillvalue='')))


@dp.message_handler(text=ButtonText.change_cohort)
async def h__any__change_cohort(msg: Message):
    regions = await wp_api.get_regions()

    await msg.answer(_('Выберите область:️'), reply_markup=create_dynamic_inline_keyboard(regions, 2, 'f/region'))


@dp.callback_query_handler(lambda c: c.data.startswith('f/region/'))
async def q__any__f_region(query: CallbackQuery):
    await query.answer()

    slug = query.data.lstrip('f/region/')

    regions = await wp_api.get_regions()

    await query.message.answer(f'Вы выбрали {dict(regions)[slug]}.\nМы Вас запомнили. Ждите 22:00. 😈')
