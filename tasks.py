import asyncio
import typing
from abc import ABC, abstractmethod

import aioschedule
from aiogram import Bot

from db import aiogram_bucket
from lang import i18n
from post import PostsFiltration


class PeriodicTask(ABC):
    def __init__(self):
        self.chat_ids: typing.List[tuple[str, str]] = self.get_user_ids()

    def get_user_ids(self) -> typing.List[tuple[str, str]]:
        user_and_locale: typing.List[tuple[str, str]] = list()

        for user in list(aiogram_bucket.find({}, {'user': 1, 'bucket.locale': 1})):
            locale = 'ru'
            if user['bucket'].get('locale'):
                locale = user['bucket']['locale']
            user_and_locale.append((user['user'], locale))
        return user_and_locale

    @abstractmethod
    async def get_bot_coroutine(self, *args, **kwargs):
        pass

    async def send(self):
        for chat_id, locale in self.chat_ids:
            i18n.ctx_locale.set(locale)
            await self.get_bot_coroutine(chat_id)

    @abstractmethod
    def every(self):
        pass


class PeriodicDailyText(PeriodicTask):
    def __init__(self, interval: int, time: str, value):
        super().__init__()
        self.interval = interval
        self.time = time
        self.value = value

    async def get_bot_coroutine(self, chat_id):
        await Bot.get_current().send_message(chat_id, self.value, disable_notification=True)

    def every(self):
        aioschedule.every(interval=self.interval).days.at(self.time).do(self.send)


class PeriodicPostSpammer(PeriodicTask):
    def __init__(self, interval: int):
        super().__init__()
        self.interval = interval

    def get_new_appartment_ids(self):
        return []

    async def get_bot_coroutine(self, chat_id):
        posts = await PostsFiltration(chat_id).find_estate()
        for post in posts:
            await Bot.get_current().send_photo(chat_id, post.get_photo_url(),
                                               post.get_description(), reply_markup=post.get_buttons())

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
