from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from database.models.user import User as DBUser

class UserManagerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: Optional[TgUser] = data.get("event_from_user")
        
        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        database_session: AsyncSession = data["session"]

        query = select(DBUser).where(DBUser.tg_id == tg_user.id)
        result = await database_session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            user = DBUser(
                tg_id=tg_user.id,
                language_code=tg_user.language_code
            )
            if tg_user.id == settings.OWNER_ID:
                user.daily_limit=999

            database_session.add(user)
            await database_session.flush()

        data["user"] = user
        data["lang"] = user.language_code
        
        return await handler(event, data)