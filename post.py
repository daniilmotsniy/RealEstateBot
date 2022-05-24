from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards import InlineButtonText
from lang import i18n

_ = __ = i18n.gettext
___ = i18n.lazy_gettext


class Post:
    CONTACT_LINK = 'https://t.me/avezor'

    # FIXME multi lang
    address = _('post_Address')
    district = 'District'
    city = 'City'
    region = 'Region'
    rooms = 'Rooms'
    area = 'Area'
    floor = 'Floor'
    price = 'Price'
    id_ = 'ID'

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
        return f'{self._name}\n{self.address}: {self._address}\nDistrict: ' \
               f'{self._district}\n{self.city}: {self._city}\n' \
                      f'{self.region}: {self._region}' \
               f'\n{self.area}: {self._area}\n{self.rooms}: {self._rooms}\n' \
                      f'{self.floor}: {self._floor}' \
               f'\n{self.price}: {self._price}\n{self.id_}: {self._post_id}'

    def get_photo_url(self):
        return self._photo
