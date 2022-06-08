import io
import typing
from typing import List, BinaryIO

import aiohttp
from PIL import Image, UnidentifiedImageError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from avbot import mem
from lang import i18n
from newapi import get_estate

_ = __ = i18n.gettext


def return_first_item_if_exists(data: dict, field: str, subfield):
    value = data.get(field)
    if value:
        return next(iter(value)).get(subfield)
    return None


class Post:
    """
    this class converts estate property by given WP API to telegram post
    """

    CONTACT_LINK = 'https://t.me/avezor'

    def __init__(self, property_data: dict):
        self._post_id = property_data.get('id')
        self._name = property_data.get('title')
        self._address = property_data.get('address')
        self._region = return_first_item_if_exists(property_data, 'area', 'name')
        self._city = return_first_item_if_exists(property_data, 'city', 'name')
        self._district = return_first_item_if_exists(property_data, 'district', 'name')
        self._area = property_data.get('square')
        self._rooms = property_data.get('room_count')
        self._floor = property_data.get('floor')
        self._price = f"{property_data.get('price')}"
        self._link = property_data.get('link')
        self._photo_link = property_data.get('image')

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

    async def get_photo_io(self) -> BinaryIO:
        return await self.convert_photo(self._photo_link)

    @staticmethod
    async def convert_photo(photo_data_link: str) -> BinaryIO:
        telegram_max_dimensions = 10_000

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(photo_data_link) as resp:
                    buffer1 = io.BytesIO(await resp.read())

            img = Image.open(buffer1)

            if img.width + img.height <= telegram_max_dimensions:
                buffer1.seek(0)

                return buffer1

            f = telegram_max_dimensions / (img.width + img.height)
            img.thumbnail((int(img.width * f), int(img.height * f)))

            buffer2 = io.BytesIO()

            img.save(buffer2, format='JPEG', quality=75)

            img.close()
            buffer1.close()
            buffer2.seek(0)

            return buffer2
        except UnidentifiedImageError:
            return open('no_photo.jpg', 'rb')


class PostsFiltration:
    MAX_ROOMS = 1000
    MIN_ROOMS = 0
    MORE_THAN_4_ROOMS_FLAG = 5

    def __init__(self, user_id: int):
        self._user_id: int = user_id

    async def find_estate(self, skip_shown: bool = True) -> List[Post]:
        """
        :return: list of compiled posts for bot
        """
        criteria = await self.get_criteria()
        if not criteria:
            return []
        if not criteria.get('query_formed', False):
            return []

        locale = criteria.get('locale')
        city = criteria.get('region')
        # Rent/Sale
        deal_type = criteria.get('action')
        # Apartment/House/Hotel/...
        property_type = criteria.get('property_type')
        post_type = criteria.get('post_type')
        estate_type = post_type or property_type
        rooms_counts: typing.List[int] = criteria.get('rooms_counts')
        rooms_from, rooms_to = self.count_rooms(rooms_counts)
        # City districts
        wards: typing.List[int] = criteria.get('wards')
        price_min = criteria.get('amount_min')
        price_max = criteria.get('amount_max')

        shown_ids = criteria.get('shown_ids') or list()
        all_properties = await get_estate(
            user_id=self._user_id,
            lang=locale,
            deal_type=deal_type,
            city=city,
            estate_type=estate_type,
            price_from=price_min,
            price_to=price_max,
            rooms_from=rooms_from,
            rooms_to=rooms_to,
        )
        if all_properties == 'not found':
            return []
        results: typing.List[Post] = list()
        for property_data in all_properties:
            property_id = property_data['id']
            district_id = return_first_item_if_exists(property_data, 'district', 'id')
            if district_id and not self.is_in_valid_districts(district_id, wards):
                continue
            if skip_shown and property_id in shown_ids:
                continue
            results.append(Post(property_data))
            shown_ids.append(property_id)
        await mem.update_bucket(user=self._user_id, shown_ids=shown_ids)
        return results

    async def get_criteria(self):
        """
        :return: user criteria for apartments
        """
        bucket = await mem.get_bucket(user=self._user_id)
        if bucket.get('query_formed') is False:
            return None
        return bucket

    def count_rooms(self, rooms_counts: typing.List[int]) -> typing.Tuple[int, int]:
        """
        :param rooms_counts: list of selected rooms
        MORE_THAN_4_ROOMS_FLAG means number from estate has more than N rooms
        :return: rooms min count, rooms max count
        """
        if rooms_counts:
            rooms_from = min(rooms_counts)
            rooms_to = max(rooms_counts)
        else:
            rooms_from = self.MIN_ROOMS
            rooms_to = self.MAX_ROOMS

        if rooms_to == self.MORE_THAN_4_ROOMS_FLAG:
            rooms_from = self.MORE_THAN_4_ROOMS_FLAG - 1
            rooms_to = self.MAX_ROOMS
        return rooms_from, rooms_to

    @staticmethod
    def is_in_valid_districts(district_id: int, wards: typing.List[int]) -> bool:
        """
        :return: if apartment district is in selected districts
        """
        if district_id not in wards:
            return False
        return True
