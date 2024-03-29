import logging
from typing import Union, Any

import aiohttp
from aiogram.types import User

from avbot import mem


async def _query(slug: str, *, country: str = None, locale: str = None, user_id: int = None,
                 **params: Union[str, int]) -> Union[dict, list]:
    if not user_id:
        user_id = User.get_current().id

    if country is None:
        country = (await mem.get_bucket(user=user_id))['country']

    if locale is None:
        locale = (await mem.get_bucket(user=user_id))['locale']

    logging.log(logging.DEBUG, f'{slug}?{params}')

    if country == 'ua':
        url = 'https://avezor.com/newapi/v1'
    elif country == 'ge':
        url = 'https://avezor.ge/newapi/v1'
    else:
        raise ValueError('Country not found')

    async with aiohttp.ClientSession() as session:
        query = f'{url}/{slug}.php?lang={locale}'

        if params:
            query += '&' + '&'.join(f'{k}={v}' for k, v in params.items())

        async with session.get(query) as resp:
            return await resp.json()


async def get_areas() -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query('get_areas')]


async def get_regions(area_id: int) -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query('get_child_regions', parent_region=area_id)]


async def get_actions() -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query('get_actions')]


async def get_nl_types(cat: str = None) -> list[tuple[int, str]]:
    if cat is None:
        return [(x['id'], x['name']) for x in await _query('get_nl_types')]
    else:
        return [(x['id'], x['name']) for x in await _query('get_nl_types', parent_cat=cat)]


async def get_wards(region_id: int) -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query('get_child_wards', parent_region=region_id)]


async def get_sub_wards(ward_id: int) -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query('get_child_subwards', parent_region=ward_id)]


async def get_estate(**params: Union[str, int]) -> list[Any]:
    return await _query('objects_query_params', **params)
