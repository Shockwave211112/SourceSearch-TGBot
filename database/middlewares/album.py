import asyncio
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

class AlbumThrottleMiddleware(BaseMiddleware):
    def __init__(self, cache_ttl: float = 5.0):
        self.album_cache = set()
        self.cache_ttl = cache_ttl

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.media_group_id is not None:
            mg_id = event.media_group_id

            if mg_id in self.album_cache:
                return

            self.album_cache.add(mg_id)

            loop = asyncio.get_running_loop()
            loop.call_later(self.cache_ttl, self.album_cache.discard, mg_id)

        return await handler(event, data)