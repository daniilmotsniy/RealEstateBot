import io
import typing
from typing import List

import requests
from PIL import Image
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from avbot import mem
from lang import i18n
from newapi import get_estate

_ = __ = i18n.gettext


class Post:
    """
    this class converts estate property by given WP API to telegram post
    """

    CONTACT_LINK = 'https://t.me/avezor'

    def __init__(self, property_data: dict):
        self._post_id = property_data.get('mls')
        self._name = property_data.get('title')['rendered']
        self._address = property_data.get('property_address')
        self._region = property_data.get('')
        self._city = property_data.get('')
        self._district = property_data.get('')
        self._area = property_data.get('property_size')
        self._rooms = property_data.get('property_rooms')
        self._floor = property_data.get('floors')
        self._price = f"{property_data.get('property_price')} {property_data.get('property_label_before')}"
        self._link = property_data.get('link')
        photo_data_link = property_data['photo'].get('')
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
        criteria = await self.get_criteria()
        if not criteria:
            return []
        if not criteria.get('query_formed', False):
            return []

        locale = criteria.get('locale')
        # Область
        area = criteria.get('area')
        # Город
        region = criteria.get('region')
        # Аренда/Продажа
        action = criteria.get('action')
        # Квартира/Дом/Гостинка/...
        property_type = criteria.get('property_type')
        # Комнаты
        rooms_counts: typing.List[int] = criteria.get('rooms_counts')
        # Районы города
        wards: typing.List[int] = criteria.get('wards')
        price_min = criteria.get('amount_min')
        price_max = criteria.get('amount_max')

        shown_ids = criteria.get('shown_ids') or list()
        # TODO new api
        all_properties = await get_estate()
        results: typing.List[Post] = list()
        for property in all_properties:
            property_id = property['id']
            if property_id in shown_ids:
                continue
            results.append(Post(property['id']))
            shown_ids.append(property_id)
        await mem.update_bucket(user=self._user_id, shown_ids=shown_ids)
        return results
