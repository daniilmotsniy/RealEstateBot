from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards import InlineButtonText
from lang import i18n

_ = __ = i18n.gettext


class Post:
    CONTACT_LINK = 'https://t.me/avezor'

    def __init__(self,
                 post_id, name, photo, address,
                 region, city, district,
                 area, rooms, floor, price, link):
        self._post_id = post_id
        self._name = name
        self._photo = photo
        self._address = address
        self._region = region
        self._city = city
        self._district = district
        self._area = area
        self._rooms = rooms
        self._floor = floor
        self._price = price
        self._link = link

    def get_buttons(self):
        write_btn = InlineKeyboardButton(InlineButtonText.write, url=self.CONTACT_LINK)
        more_btn = InlineKeyboardButton(InlineButtonText.more, url=self._link)
        return InlineKeyboardMarkup().add(write_btn, more_btn)

    def get_description(self):
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

    def get_photo_url(self):
        return self._photo
