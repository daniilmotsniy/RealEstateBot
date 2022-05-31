import io
from typing import List

import requests
from PIL import Image
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from avbot import mem
from lang import i18n
from wp_api import get_estate

_ = __ = i18n.gettext


class Post:
    """
    this class converts estate property by given WP API to telegram post
    """

    CONTACT_LINK = 'https://t.me/avezor'

    def __init__(self, estate_id: str, locale: str):
        def get_taxonomy(api: str):
            return next(iter(requests.get(f'{api}={estate_id}', verify=False).json())).get('name')

        api_prefix = 'https://avezor.com/wp-json/wp/v2/'
        if locale == 'ka':
            api_prefix = 'https://avezor.ge/wp-json/wp/v2/'

        estate_api = api_prefix + 'estate_property'
        region_api = api_prefix + 'property_county_state?post'
        city_api = api_prefix + 'property_city?post'
        district_api = api_prefix + 'property_area?post'

        property_data = requests.get(f'{estate_api}/{estate_id}', verify=False).json()
        self._post_id = property_data.get('mls')
        self._name = property_data.get('title')['rendered']
        self._address = property_data.get('property_address')
        self._region = get_taxonomy(region_api)
        self._city = get_taxonomy(city_api)
        self._district = get_taxonomy(district_api)
        self._area = property_data.get('property_size')
        self._rooms = property_data.get('property_rooms')
        self._floor = property_data.get('floors')
        self._price = f"{property_data.get('property_price')} {property_data.get('property_label_before')}"
        self._link = property_data.get('link')

        photo_data_link = next(iter(property_data['_links'].get('wp:attachment'))).get('href')
        self._photo = self.convert_photo(photo_data_link)

    def get_buttons(self) -> InlineKeyboardMarkup:
        write_btn = InlineKeyboardButton(_("Написать"), url=self.CONTACT_LINK)
        more_btn = InlineKeyboardButton(_("Подробнее"), url=self._link)
        return InlineKeyboardMarkup().add(write_btn, more_btn)

    def get_description(self) -> str:
        return f'{self._name}\n' + \
               _('post_Address') + f': {self._address}\n' + \
               _('post_District') + f': {self._district}\n' + \
               _('post_City') + f': {self._city}\n' + \
               _('post_Region') + f': {self._region}\n' + \
               _('post_Area') + f': {self._area}\n' + \
               _('post_Rooms') + f': {self._rooms}\n' + \
               _('post_Floor') + f': {self._floor}\n' + \
               _('post_Price') + f': {self._price}\n' + \
               _('post_ID') + f': {self._post_id}'

    def get_photo_url(self) -> memoryview:
        return self._photo

    @staticmethod
    def convert_photo(photo_data_link: str) -> memoryview:
        photo_link = next(iter(
            requests.get(photo_data_link, verify=False).json()
        )).get('media_details').get('sizes').get('medium').get('s3').get('url')
        img = Image.open(requests.get(photo_link, stream=True).raw)
        photo_buffer = io.BytesIO()
        img.save(photo_buffer, format='JPEG', quality=75)
        return photo_buffer.getbuffer()


class PostsFiltration:
    def __init__(self, user_id: int):
        self._user_id: int = user_id

    async def get_criteria(self):
        bucket = await mem.get_bucket(user=self._user_id)
        if bucket.get('query_formed') is False:
            return None
        return bucket

    async def find_estate(self) -> List[Post]:
        results = list()
        criteria = await self.get_criteria()
        if not criteria:
            return []
        shown_ids = criteria.get('shown_ids') or list()
        all_objects = await get_estate()
        for obj in all_objects:
            if obj['id'] in shown_ids:
                continue
            price = int(obj['property_price'])
            rooms = int(obj['property_rooms'])
            region = obj.get('property_county_state')
            deal_type = obj.get('property_action_category')
            if criteria.get('amount_min') and criteria.get('amount_max'):
                if criteria['amount_min'] >= price or criteria['amount_max'] <= price:
                    continue
            if rooms > 0 and criteria.get('room_counts'):
                if rooms not in criteria['room_counts']:
                    continue
            if criteria.get('region') and len(region) > 0:
                if region[0] != criteria['region']:
                    continue
            if criteria.get('deal_type') and len(deal_type) > 0:
                if deal_type[0] != criteria['deal_type']:
                    continue
            results.append(Post(obj['id'], criteria['locale']))
            shown_ids.append(obj['id'])
        await mem.update_bucket(user=self._user_id, shown_ids=shown_ids)
        return results
