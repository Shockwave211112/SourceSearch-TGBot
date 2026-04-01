from datetime import datetime
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.answer_utils import get_text, ActionCallbackData


class ThrottlingMiddleware(BaseMiddleware):
    """
    Мидлварь для предотвращения спама запросами юзера к API
    """
    def __init__(self, slow_mode_delay: float = 5):
        self.delay = slow_mode_delay

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        user = data.get("user")
        if not user:
            return await handler(event, data)

        now = datetime.now()
        lang = data.get("lang")
        if user.last_request:
            delta = (now - user.last_request).total_seconds()
            if delta < self.delay:
                seconds_left = int(self.delay - delta)
                text = f"{get_text('MESSAGES', 'THROTTLE_ERROR', lang)} ({seconds_left}s)"

                if isinstance(event, CallbackQuery):
                    return await event.answer(text)

                kb = None
                if event.photo:
                    builder = InlineKeyboardBuilder()
                    builder.button(
                        text=get_text("BUTTONS", "TRY_AGAIN", lang),
                        callback_data=ActionCallbackData(action="search_again", next_provider=None)
                    )
                    kb = builder.as_markup()

                method = event.reply if event.photo else event.answer
                return await method(text, reply_markup=kb)

        return await handler(event, data)