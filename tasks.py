import asyncio
import typing
from abc import ABC, abstractmethod
from datetime import datetime

import aioschedule
import pytz
from pytz import timezone
from aiogram import Bot

from db import aiogram_bucket
from lang import i18n
from post import PostsFiltration, Post


class PeriodicTask(ABC):
    DO_NOT_DISTURB_AFTER = 22

    def __init__(self):
        self.chat_ids: typing.List[tuple[int, str, str]] = self.find_users()
        self.country_2_tz = {
            'ua': 'Etc/GMT-3',
            'ge': 'Etc/GMT-4',
        }

    @staticmethod
    def find_users() -> typing.List[tuple[int, str, str]]:
        user_info: typing.List[tuple[int, str, str]] = list()

        for user in list(aiogram_bucket.find({}, {'user': 1, 'bucket.locale': 1, 'bucket.country': 1})):
            user_id = user['user']
            locale = 'ru'
            country = 'ua'
            if user['bucket'].get('locale'):
                locale = user['bucket']['locale']
                country = user['bucket']['country']
            user_info.append((user_id, locale, country))
        return user_info

    @abstractmethod
    async def get_bot_coroutine(self, *args, **kwargs):
        pass

    def do_not_disturb_mode(self, country: str):
        time_zone = self.country_2_tz.get(country, 'ua')
        tz = timezone(time_zone)
        utc_time = datetime.now().utcnow()
        now = utc_time.replace(tzinfo=pytz.utc).astimezone(tz)
        return now.hour >= self.DO_NOT_DISTURB_AFTER

    async def send(self):
        for chat_id, locale, country in self.chat_ids:
            i18n.ctx_locale.set(locale)
            await self.get_bot_coroutine(
                chat_id,
                do_not_disturb_mode=self.do_not_disturb_mode(country)
            )

    @abstractmethod
    def every(self):
        pass


class PeriodicDailyText(PeriodicTask):
    def __init__(self, interval: int, time: str, value):
        super().__init__()
        self.interval = interval
        self.time = time
        self.value = value

    async def get_bot_coroutine(self, chat_id: int, do_not_disturb_mode: bool = False):
        await Bot.get_current().send_message(chat_id, self.value, disable_notification=do_not_disturb_mode)

    def every(self):
        aioschedule.every(interval=self.interval).days.at(self.time).do(self.send)


class PeriodicPostSpammer(PeriodicTask):
    def __init__(self, interval: int):
        super().__init__()
        self.interval: int = interval

    async def get_bot_coroutine(self, chat_id: int, do_not_disturb_mode: bool = False):
        posts: typing.List[Post] = await PostsFiltration(chat_id).find_estate()
        for post in posts:
            await Bot.get_current().send_photo(chat_id, post.get_photo_url(),
                                               post.get_description(),
                                               reply_markup=post.get_buttons(),
                                               disable_notification=do_not_disturb_mode)

    def every(self):
        aioschedule.every(interval=self.interval).minutes.do(self.send)


class Scheduler:
    def __init__(self, *tasks: PeriodicTask):
        self.tasks = tasks

    async def schedule(self):
        [task.every() for task in self.tasks]
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(aioschedule.idle_seconds())

    async def get_periodic_tasks(self, _):
        asyncio.create_task(self.schedule())
