import asyncio
import typing

import aioschedule
from aiogram import Bot


class PeriodicTask:
    def __init__(self, bot: Bot, days: int, time: str, text: str):
        self.bot = bot
        self.days = days
        self.time = time
        self.text = text
        # FIXME add mongo ids
        self.chat_ids: typing.List[str] = ['522343041']

    async def send_msg(self):
        for chat_id in self.chat_ids:
            await self.bot.send_message(chat_id, self.text)

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

    async def on_startup(self, _):
        asyncio.create_task(self.schedule())
