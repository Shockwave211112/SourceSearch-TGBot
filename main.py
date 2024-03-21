from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ContentType

from core.handlers.basic import get_start, get_photo, get_anything, get_group_message
from core.settings import settings

import asyncio

async def start():
    bot = Bot(token=settings.tokens.bot_token)

    dp = Dispatcher()
    
    dp.message.register(get_start, F.text == "/start")
    dp.message.register(get_group_message, F.photo, F.chat.type == ["group"])
    dp.message.register(get_photo, F.photo, F.chat.type == "private")
    dp.message.register(get_anything)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        
if __name__ == "__main__":
    asyncio.run(start())