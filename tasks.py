import asyncio
import typing

import aioschedule
from aiogram import Bot

from lang import i18n


class PeriodicTask:
    def __init__(self, days: int, time: str, text):
        self.days = days
        self.time = time
        self.text = text
        # FIXME add mongo ids
        self.chat_ids: typing.List[tuple[str, str]] = [('608815116', 'ru')]

    async def send_msg(self):
        for chat_id, locale in self.chat_ids:
            i18n.ctx_locale.set(locale)
            await Bot.get_current().send_message(chat_id, self.text, disable_notification=True)

    def every(self):
        aioschedule.every(interval=self.days).days.at(self.time).do(self.send_msg)


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
