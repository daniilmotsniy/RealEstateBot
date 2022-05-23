import asyncio
import aioschedule
from aiogram import Bot


class Scheduler:
    SLEEP_TIME = 1

    def __init__(self, bot: Bot, time: str, text: str):
        self.bot = bot
        self.time = time
        self.text = text
        # FIXME add mongo ids
        self.chat_ids = ['522343041']

    async def schedule(self):
        aioschedule.every().day.at(self.time).do(self.send_msg)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(self.SLEEP_TIME)

    async def send_msg(self):
        for chat_id in self.chat_ids:
            await self.bot.send_message(chat_id, self.text)


class TelegramPeriodicTask:
    def __init__(self, *schedulers: Scheduler):
        self.schedulers = schedulers

    async def on_startup(self, _):
        [asyncio.create_task(scheduler.schedule()) for scheduler in self.schedulers]
