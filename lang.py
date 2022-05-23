from pathlib import Path
from typing import Any, Tuple, Optional

from aiogram import Dispatcher
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.types import User


class LocaleMiddleware(I18nMiddleware):
    def __init__(self, domain: str, path: Path):
        super(LocaleMiddleware, self).__init__(domain, path, default='ru')

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user: Optional[User] = User.get_current()

        if user:
            mem = Dispatcher.get_current().storage
            bucket = await mem.get_bucket(user=user.id)

            locale = bucket.get('locale', None)

            if locale:
                args[-1]['locale'] = locale

                return locale

        return await super().get_user_locale(action, args)

    async def set_locale(self, user: User, locale: str):
        if locale not in self.locales:
            return False

        mem = Dispatcher.get_current().storage
        await mem.update_bucket(user=user.id, locale=locale)
        self.ctx_locale.set(locale)

        return True


i18n = LocaleMiddleware('bot', Path(__file__).parent / 'locales')
