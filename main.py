import asyncio
import logging
from aiogram import Bot, Dispatcher
from core.config import settings
from database.config import async_session, init_db
from database.middlewares.album import AlbumThrottleMiddleware
from database.middlewares.throttle import ThrottlingMiddleware
from handlers.main import router
from database.middlewares.session import DbSessionMiddleware
from database.middlewares.user import UserManagerMiddleware
from utils.logging_utils import SensitiveDataFilter

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    sec_filter = SensitiveDataFilter(sensitive_words=[settings.SAUCENAO_API_KEY, settings.BOT_TOKEN, settings.DANBOORU_API_KEY])

    logger = logging.getLogger()
    for handler in logger.handlers:
        handler.addFilter(sec_filter)

async def main():
    await init_db()

    setup_logging()
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher()

    dp.message.outer_middleware(AlbumThrottleMiddleware())
    dp.message.outer_middleware(DbSessionMiddleware(database_session=async_session))
    dp.message.outer_middleware(UserManagerMiddleware())
    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.callback_query.outer_middleware(DbSessionMiddleware(database_session=async_session))
    dp.callback_query.outer_middleware(UserManagerMiddleware())
    dp.callback_query.outer_middleware(ThrottlingMiddleware())
    
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())