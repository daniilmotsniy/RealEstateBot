import asyncio
import itertools
from typing import Sequence, Union

from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import newapi
from avbot import dp, mem
from keyboards import ButtonText
from lang import i18n
from post import PostsFiltration, Post

_ = __ = i18n.gettext


def create_dynamic_inline_keyboard(values: Sequence[tuple[Union[str, int], Union[str, int]]], cols: int, domain: str, back: bool = False):
    length = len(values)

    if back:
        values = itertools.chain(values, [('back', _('back'))])

        length += 1

    values = [InlineKeyboardButton(str(text), callback_data=f'{domain}/{slug}') for slug, text in values]

    kb = list(itertools.chain(zip(*(itertools.repeat(iter(values), cols))), (tuple(values[-(length % cols):]),) if length % cols else ()))

    return InlineKeyboardMarkup(cols, kb)


def create_multiple_choice_keyboard(values: Sequence[tuple[Union[str, int], Union[str, int]]], selected: Sequence[Union[str, int]], cols: int, domain: str, allow_nothing: bool = True, select_all: bool = False, back: bool = False):
    selected_count = sum(slug in selected for slug, text in values)
    all_selected = selected_count == len(values)
    values = ((slug, f"{'✅' if slug in selected else '◽️'} {text}") for slug, text in values)

    return create_dynamic_inline_keyboard(list(
        itertools.chain(values,
                        (('all', _('unselectAll') if all_selected else _('selectAll')),) if select_all else (),
                        (('next', _('next')),) if allow_nothing or selected_count else ())
    ), cols, domain, back=back)


def _dict(text: str, buttons: Sequence[tuple[Union[str, int], Union[str, int]]], domain: str, cols: int = 2, back: bool = False):
    return dict(text=text, reply_markup=create_dynamic_inline_keyboard(buttons, cols, domain, back=back))


async def _edit(query: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup):
    await query.message.edit_text(text, reply_markup=reply_markup)


def _get_currency(bucket: dict) -> str:
    return _("местной валюте") if bucket['action'] == 180 else _("долларах")


async def p__area():
    areas = await newapi.get_areas()

    return {'text': _('Выберите область:️'), 'reply_markup': create_dynamic_inline_keyboard(areas, 2, 'f/area')}


async def p__region(slug: int = None):
    if slug is None:
        bucket = await mem.get_bucket(user=User.get_current().id)

        slug = bucket['area']

    regions = [(_id, name) for _id, name in await newapi.get_regions(slug) if name != 'all']

    return _dict(_("Выберите город:"), regions, 'f/region', back=True)


async def p__actions():
    actions = await newapi.get_actions()

    return _dict(_("Что Вас интересует?"), actions, 'f/actions', back=True)


async def p__post_type():
    cat_types = await newapi.get_nl_types()

    return _dict(_("Выберите категорию:"), cat_types, 'f/postType', back=True)


async def p__prop_type(slug: int = None):
    if slug is None:
        bucket = await mem.get_bucket(user=User.get_current().id)

        slug = bucket['post_type']

    types = await newapi.get_nl_types(slug)

    return _dict(_("Выберите тип объекта:"), types, 'f/propType', back=True)


async def p__room_counts():
    bucket = await mem.get_bucket(user=User.get_current().id)

    room_counts = bucket.get('room_counts', [])

    return dict(text=_("Сколько должно быть комнат в квартире?"), reply_markup=create_multiple_choice_keyboard([
        (i, '5+' if i == 5 else i) for i in range(1, 6)
    ], room_counts, 2, 'f/roomCounts', allow_nothing=False, select_all=True, back=True))


async def p__wards(region_id: int = None):
    bucket = await mem.get_bucket(user=User.get_current().id)

    if region_id is None:
        region_id = bucket['region']

    cat_types = await newapi.get_wards(region_id)

    wards = bucket.get('wards', [])

    return dict(text=_("Выберите район:"), reply_markup=create_multiple_choice_keyboard(
        cat_types, wards, 2, 'f/ward', allow_nothing=False, select_all=True, back=True))


@dp.message_handler(text=ButtonText.change_cohort)
async def h__any__change_cohort(msg: Message):
    await mem.update_bucket(user=msg.from_user.id, query_formed=False)

    await msg.answer(**await p__area())


@dp.callback_query_handler(regexp='^f/[a-zA-z]+/back$')
async def q__back(query: CallbackQuery):
    slug = query.data.split('/')[1]

    if slug == 'region':
        await _edit(query, **await p__area())
    elif slug == 'actions':
        await _edit(query, **await p__region())
    elif slug == 'postType':
        await _edit(query, **await p__actions())
    elif slug == 'propType':
        await _edit(query, **await p__post_type())
    elif slug == 'roomCounts':
        await _edit(query, **await p__prop_type())
    elif slug == 'ward':
        await _edit(query, **await p__post_type())
    elif slug == 'checkAmount':
        await _edit(query, **await p__wards())
    else:
        raise CancelHandler()


@dp.callback_query_handler(lambda c: c.data.startswith('f/area/'))
async def q__any__f_area(query: CallbackQuery):
    area_id = int(query.data.removeprefix('f/area/'))

    await mem.update_bucket(user=query.from_user.id, area=area_id)

    await _edit(query, ** await p__region(area_id))


@dp.callback_query_handler(lambda c: c.data.startswith('f/region/'))
async def q__any__f_region(query: CallbackQuery):
    s_slug = query.data.removeprefix('f/region/')

    region_id = int(s_slug)

    await mem.update_bucket(user=query.from_user.id, region=region_id)

    await _edit(query, **await p__actions())


@dp.callback_query_handler(lambda c: c.data.startswith('f/actions/'))
async def q__any__f_actions(query: CallbackQuery):
    s_slug = query.data.removeprefix('f/actions/')

    action_id = int(s_slug)

    await mem.update_bucket(user=query.from_user.id, action=action_id)

    await _edit(query, **await p__post_type())


@dp.callback_query_handler(lambda c: c.data.startswith('f/postType/'))
async def q__any__f_post_type(query: CallbackQuery):
    s_slug = query.data.removeprefix('f/postType/')

    slug = int(s_slug)

    await mem.update_bucket(user=query.from_user.id, post_type=slug)

    if slug == 178 or slug == 279:  # housing or commercial
        await _edit(query, **await p__prop_type(slug))
    else:
        await mem.update_bucket(user=query.from_user.id, property_type=None)

        await _edit(query, **await p__wards())


@dp.callback_query_handler(lambda c: c.data.startswith('f/propType/'))
async def q__any__f_prop_type(query: CallbackQuery):
    s_slug = query.data.removeprefix('f/propType/')

    slug = int(s_slug)

    await mem.update_bucket(user=query.from_user.id, property_type=slug)

    if slug == 300:  # kvartira
        await _edit(query, **await p__room_counts())
    else:
        await _edit(query, **await p__wards())


@dp.callback_query_handler(lambda c: c.data.startswith('f/roomCounts/'))
async def q__any__f_room_counts(query: CallbackQuery):
    slug = query.data.removeprefix('f/roomCounts/')

    if slug == 'next':
        await _edit(query, **await p__wards())
        return

    bucket = await mem.get_bucket(user=query.from_user.id)

    if slug == 'all':
        if set(bucket.get('room_counts', ())) == set(range(1, 6)):
            room_counts = []
        else:
            room_counts = list(range(1, 6))
    else:
        room_counts = list(set(bucket.get('room_counts', ())) ^ {int(slug)})

    await mem.update_bucket(user=query.from_user.id, room_counts=room_counts)

    await _edit(query, **await p__room_counts())


@dp.callback_query_handler(lambda c: c.data.startswith('f/ward/'))
async def q__any__f_ward(query: CallbackQuery):
    slug = query.data.removeprefix('f/ward/')

    if slug == 'next':
        await _query_amount(query)
        return

    bucket = await mem.get_bucket(user=query.from_user.id)

    all_ward_ids = [k for k, v in await newapi.get_wards(bucket['region'])]

    if slug == 'all':
        if set(bucket.get('wards', ())) == set(all_ward_ids):
            wards = []
        else:
            wards = all_ward_ids
    else:
        wards = list((set(bucket.get('wards', ())) ^ {int(slug)}) & set(all_ward_ids))

    await mem.update_bucket(user=query.from_user.id, wards=wards)

    await _edit(query, **await p__wards(bucket['region']))


async def _query_amount(query: CallbackQuery):
    bucket = await mem.get_bucket(user=query.from_user.id)

    currency = _get_currency(bucket)

    await mem.update_bucket(user=query.from_user.id, amount_min=None, amount_max=None)

    await query.message.edit_text(__("Укажите ниже минимальную сумму в {currency}.").format(currency=currency))


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
                    await msg.answer(_("Укажите ниже сумму в долларах не более 100000000."))

    raise ValueError('Cannot set amount')


@dp.message_handler(regexp='^[0-9]+$')
async def h__any__amount(msg: Message):
    try:
        if await _try_to_set_amount(msg):
            bucket = await mem.get_bucket(user=msg.from_user.id)

            currency = _get_currency(bucket)
            await msg.answer(__("Указна сумма от {amount_min} до {amount_max} в {currency}.").format(
                amount_min=bucket['amount_min'], amount_max=bucket['amount_max'],
                currency=currency
            ), reply_markup=create_dynamic_inline_keyboard(
                (('edit', "Изменить сумму"), ('next', "Далее")), 2, 'f/checkAmount', back=True)
            )
        else:
            bucket = await mem.get_bucket(user=msg.from_user.id)

            currency = _get_currency(bucket)
            await msg.answer(__("Укажите ниже максимальную сумму в {currency}").format(currency=currency))
    except ValueError:
        await msg.answer(_("Something's wrong, I can feel it."))


@dp.callback_query_handler(lambda c: c.data.startswith('f/checkAmount/'))
async def q__any__f_check_amount(query: CallbackQuery):
    await query.answer()

    slug = query.data.removeprefix('f/checkAmount/')

    if slug == 'edit':
        bucket = await mem.get_bucket(user=query.from_user.id)

        currency = _get_currency(bucket)

        await mem.update_bucket(user=query.from_user.id, amount_min=None, amount_max=None)
        await query.message.edit_text(__("Укажите ниже минимальную сумму в {currency}").format(currency=currency))
    elif slug == 'next':
        await mem.update_bucket(user=query.from_user.id, query_formed=True)

        await _show_results(query)
    else:
        raise ValueError('Unknown action')


async def _show_posts(msg: Message, posts: Sequence[Post]):
    for post, photo in zip(posts, await asyncio.gather(*(post.get_photo_io() for post in posts))):
        try:
            await msg.answer_photo(photo, post.get_description(), reply_markup=post.get_buttons())
        finally:
            photo.close()


async def _show_results(query: CallbackQuery):
    msg = query.message
    await msg.answer(_("Вот, что я нашел по Вашему запросу."))
    posts = await PostsFiltration(query.from_user.id).find_estate(skip_shown=False)
    posts_len = len(posts)
    if posts_len:
        await msg.answer(__("I have found {posts_len} post! Wait, I am sending...", "I have found {posts_len} posts! Wait, I am sending...").format(posts_len=posts_len))
    else:
        await msg.answer(_("I have not found any posts. Try later or use different filters."))

    await _show_posts(msg, posts[:20])

    if posts_len > 20:
        await msg.answer(_("Show more posts"), reply_markup=InlineKeyboardMarkup(1, [[InlineKeyboardButton(_("Показать еще"), callback_data='f/pagination/20')]]))


@dp.callback_query_handler(lambda c: c.data.startswith('f/pagination/'))
async def q__any__f_check_amount(query: CallbackQuery):
    await query.answer()

    shown = int(query.data.removeprefix('f/pagination/'))

    posts = await PostsFiltration(query.from_user.id).find_estate(skip_shown=False)

    msg = query.message

    await _show_posts(msg, posts[shown:shown + 20])

    if shown + 20 < len(posts):
        await msg.answer(_("Show more posts"), reply_markup=InlineKeyboardMarkup(1, [[InlineKeyboardButton(_("Показать еще"), callback_data=f'f/pagination/{shown + 20}')]]))

