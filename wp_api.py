from typing import Union

import aiohttp

from lang import i18n


async def _query_wp(slug: str, country: str) -> Union[dict, list]:
    if country == 'uk':
        url = 'https://avezor.com/wp-json/wp/v2/'
    elif country == 'ka':
        url = 'https://avezor.ge/wp-json/wp/v2/'
    else:
        raise ValueError('Country not found')

    async with aiohttp.ClientSession() as session:
        async with session.get(url + slug) as resp:
            return await resp.json()


async def get_regions() -> list[tuple[str, str]]:
    return [(x['slug'], x['name']) for x in await _query_wp('property_county_state', i18n.ctx_locale.get())]
