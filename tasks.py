import asyncio
import typing

import aioschedule
from aiogram import Bot

from db import aiogram_bucket
from lang import i18n


class PeriodicTask:
    def __init__(self, interval: int, time: str, value):
        self.interval = interval
        self.time = time
        self.value = value
        self.chat_ids: typing.List[tuple[str, str]] = self.get_user_ids()

    def get_user_ids(self) -> typing.List[tuple[str, str]]:
        user_and_locale = list()
        for user in list(aiogram_bucket.find({}, {'user': 1, 'bucket.locale': 1})):
            locale = 'uk'
            if user['bucket'].get('locale'):
                locale = user['bucket']['locale']
            user_and_locale.append((user['user'], locale))
        return user_and_locale

    async def send_msg(self):
        for chat_id, locale in self.chat_ids:
            i18n.ctx_locale.set(locale)
            await Bot.get_current().send_message(chat_id, self.value, disable_notification=True)

    def every(self):
        aioschedule.every(interval=self.interval).days.at(self.time).do(self.send_msg)


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
