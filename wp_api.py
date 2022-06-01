from typing import Union, Any

import aiohttp
from aiogram.types import User

from avbot import mem


async def _query_wp(slug: str, country: str = None) -> Union[dict, list]:
    if country is None:
        country = (await mem.get_bucket(user=User.get_current().id))['country']

    if country == 'ua':
        url = 'https://avezor.com/wp-json/wp/v2/'
    elif country == 'ge':
        url = 'https://avezor.ge/wp-json/wp/v2/'
    else:
        raise ValueError('Country not found')

    async with aiohttp.ClientSession() as session:
        async with session.get(url + slug) as resp:
            return await resp.json()


async def get_regions() -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query_wp('property_county_state')]


async def get_districts(region_name: str) -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query_wp('property_city') if x['stateparent'] == region_name]


async def get_action_types() -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query_wp('property_action_category')]


async def get_property_types() -> list[tuple[int, str]]:
    return [(x['id'], x['name']) for x in await _query_wp('property_category')]


async def get_estate() -> list[Any]:
    return await _query_wp('estate_property')
