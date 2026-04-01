from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, database_session):
        self.database_session = database_session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.database_session() as database_session:
            data["session"] = database_session
            try:
                result = await handler(event, data)
                await database_session.commit()
                return result
            except Exception:
                await database_session.rollback()
                raise