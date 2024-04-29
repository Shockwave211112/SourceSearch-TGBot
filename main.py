from aiogram import Bot, Dispatcher
from core.handlers import main
from core.settings import settings
import asyncio

async def start():
    bot = Bot(token=settings.tokens.bot_token)

    dp = Dispatcher()
    
    dp.include_router(main.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        
if __name__ == "__main__":
    asyncio.run(start())