from aiogram import Bot

from db import aiogram_bucket


class SpamToUsers:
    def __init__(self, country: str, locale: str, message: str):
        self._country = country
        self._locale = locale
        self._message = message

    async def spam(self):
        for user in list(aiogram_bucket.find({}, {'user': 1, 'bucket.locale': 1, 'bucket.country': 1})):
            if user['bucket'].get('locale') and user['bucket']['locale'] != self._locale:
                continue
            if user['bucket'].get('country') and user['bucket']['country'] != self._country:
                continue
            await Bot.get_current().send_message(user['user'], self._message)
