import io

import requests
from PIL import Image
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lang import i18n

_ = __ = i18n.gettext


class Post:
    """
    this class converts estate property by given WP API to telegram post
    """

    CONTACT_LINK = 'https://t.me/avezor'

    def __init__(self, estate_id, domain):
        def get_taxonomy(api: str):
            return next(iter(requests.get(f'{api}={estate_id}', verify=False).json())).get('name')

        api_prefix = f'https://avezor.{domain}/wp-json/wp/v2/'
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
