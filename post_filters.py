import itertools
from typing import Sequence, Union

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import wp_api
from avbot import dp, mem, bot
from keyboards import ButtonText
from lang import i18n
from post import PostsFiltration

_ = __ = i18n.gettext


def create_dynamic_inline_keyboard(values: Sequence[tuple[Union[str, int], Union[str, int]]], cols: int, domain: str, back: bool = False):
    length = len(values)

    if back:
        values = itertools.chain(values, [('back', _('back'))])

        length += 1

    values = [InlineKeyboardButton(str(text), callback_data=f'{domain}/{slug}') for slug, text in values]

    kb = list(itertools.chain(zip(*(itertools.repeat(iter(values), cols))), (tuple(values[-(length % cols):]),) if length % cols else ()))

    return InlineKeyboardMarkup(cols, kb)


async def _edit_msg(query: CallbackQuery, text: str, buttons: Sequence[tuple[Union[str, int], Union[str, int]]], domain: str, cols: int = 2, back: bool = False):
    await query.message.edit_text(text, reply_markup=create_dynamic_inline_keyboard(buttons, cols, domain, back=back))


def _get_currency(bucket: dict) -> str:
    return 'гривне' if bucket['deal_type'] == 180 else 'долларах'


@dp.message_handler(text=ButtonText.change_cohort)
async def h__any__change_cohort(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, query_formed=False)

    regions = await wp_api.get_regions()

    await msg.answer(_('Выберите область:️'), reply_markup=create_dynamic_inline_keyboard(regions, 2, 'f/region'))


@dp.callback_query_handler(lambda c: c.data.startswith('f/region/'))
async def q__any__f_region(query: CallbackQuery):
    slug = int(query.data.removeprefix('f/region/'))

    await mem.update_bucket(user=query.from_user.id, region=slug)

    regions = await wp_api.get_regions()

    region_name = dict(regions)[slug]

    districts = [(_id, name) for _id, name in await wp_api.get_districts(region_name) if name != 'all']

    await _edit_msg(query, "Выберите район:", districts, 'f/district', back=True)


@dp.callback_query_handler(lambda c: c.data.startswith('f/district/'))
async def q__any__f_district(query: CallbackQuery):
    slug = int(query.data.removeprefix('f/district/'))

    await mem.update_bucket(user=query.from_user.id, district=slug)

    action_types = await wp_api.get_action_types()

    await _edit_msg(query, "Что Вас интересует?", action_types, 'f/actionType', back=True)


@dp.callback_query_handler(lambda c: c.data.startswith('f/actionType/'))
async def q__any__f_district(query: CallbackQuery):
    slug = int(query.data.removeprefix('f/actionType/'))

    await mem.update_bucket(user=query.from_user.id, deal_type=slug)

    await _edit_msg(query, "Выберите категорию:", (('housing', _('housing')), ('land', _('land')), ('commercial', _('commercial'))), 'f/postType', back=True)


@dp.callback_query_handler(lambda c: c.data.startswith('f/postType/'))
async def q__any__f_district(query: CallbackQuery):
    await query.answer()

    slug = query.data.removeprefix('f/postType/')

    await mem.update_bucket(user=query.from_user.id, post_type=slug)

    if slug == 'housing' or slug == 'commercial':
        types = dict(await wp_api.get_property_types())

        # TODO
        del types[178]  # zhiloj-fond
        del types[274]  # zemlya

        filtered_types = []  # TODO

        for k, name in types.items():
            # if k in {'gostinka', 'dacha', 'doma', 'kvartira'}:
            if k in {179, 202, 247, 300}:
                if slug == 'housing':
                    filtered_types.append((k, name))
            elif slug == 'commercial':
                filtered_types.append((k, name))

        await _edit_msg(query, "Выберите тип объекта:", filtered_types, 'f/propType', back=True)
    elif slug == 'land':
        await _query_city(query)
    else:
        raise ValueError('Unknown post type')


@dp.callback_query_handler(lambda c: c.data.startswith('f/propType/'))
async def q__any__f_district(query: CallbackQuery):
    slug = int(query.data.removeprefix('f/propType/'))

    await mem.update_bucket(user=query.from_user.id, property_type=slug)

    if slug == 300:  # kvartira
        room_counts = await wp_api.get_room_counts()

        await _edit_msg(query, "Сколько должно быть комнат в квартире?", room_counts, 'f/roomCounts', back=True)
    else:
        await _query_city(query)


@dp.callback_query_handler(lambda c: c.data.startswith('f/roomCounts/'))
async def q__any__f_district(query: CallbackQuery):
    slug = int(query.data.removeprefix('f/roomCounts/'))

    await mem.update_bucket(user=query.from_user.id, room_counts=[slug])

    await _query_city(query)


async def _query_city(query: CallbackQuery):
    bucket = await mem.get_bucket(user=query.from_user.id)

    currency = _get_currency(bucket)

    await mem.update_bucket(user=query.from_user.id, amount_min=None, amount_max=None)

    await query.message.edit_text(f"Может Вы не заметили, но Вы только что выбрали все районы. )\n\nУкажите ниже минимальную сумму в {currency}.")


async def _try_to_set_amount(msg: Message) -> bool:
    bucket = await mem.get_bucket(user=msg.from_user.id)

    amount = int(msg.text)

    if bucket.get('query_formed') is False:
        if 'amount_min' in bucket:
            if bucket['amount_min'] is None:
                await mem.update_bucket(user=msg.from_user.id, amount_min=amount)
                return False
            if bucket['amount_max'] is None:
                if amount < 100000000:
                    await mem.update_bucket(user=msg.from_user.id, amount_max=amount)
                    return True
                else:
                    await msg.answer("Укажите ниже сумму в долларах не более 100000000.")

    raise ValueError('Cannot set amount')


@dp.message_handler(regexp='^[0-9]+$')
async def h__any__amount(msg: Message):
    try:
        if await _try_to_set_amount(msg):
            bucket = await mem.get_bucket(user=msg.from_user.id)

            currency = _get_currency(bucket)

            await msg.answer(f"Указна сумма от {bucket['amount_min']} до {bucket['amount_max']} в {currency}", reply_markup=create_dynamic_inline_keyboard((('edit', "Изменить сумму"), ('next', "Далее")), 2, 'f/checkAmount', back=True))
        else:
            bucket = await mem.get_bucket(user=msg.from_user.id)

            currency = _get_currency(bucket)

            await msg.answer(f"Укажите ниже максимальную сумму в {currency}.")
    except ValueError:
        await msg.answer(_("Something's wrong, I can feel it."))


@dp.callback_query_handler(lambda c: c.data.startswith('f/checkAmount/'))
async def q__any__f_district(query: CallbackQuery):
    await query.answer()

    slug = query.data.removeprefix('f/checkAmount/')

    if slug == 'edit':
        bucket = await mem.get_bucket(user=query.from_user.id)

        currency = _get_currency(bucket)

        await mem.update_bucket(user=query.from_user.id, amount_min=None, amount_max=None)

        await query.message.edit_text(f"Укажите ниже минимальную сумму в {currency}.")
    elif slug == 'next':
        await mem.update_bucket(user=query.from_user.id, query_formed=True)

        await _show_results(query)
    else:
        raise ValueError('Unknown action')


async def _show_results(query: CallbackQuery):
    await query.message.answer("Вот, что я нашел по Вашему запросу.\nМы Вас запомнили. Ждите 22:00. 😈")
    posts = await PostsFiltration(query.from_user.id).find_estate()
    for post in posts:
        await bot.send_photo(query.message.chat.id, post.get_photo_url(),
                             post.get_description(), reply_markup=post.get_buttons())
