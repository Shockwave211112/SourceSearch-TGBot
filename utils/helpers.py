import logging
from core.config import settings
from typing import Optional, Union
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)

def check_useless_hostname(current_value: str):
    if current_value in settings.USELESS_HOSTS:
        return True
    return False

class SmartResponse:
    """
    Хэлпер для ответа/редактирования сообщения без ifelsetrycatch по коду
    """
    def __init__(self, event: Union[Message, CallbackQuery]):
        if isinstance(event, CallbackQuery):
            self.accepted_msg = event.message
            self.sent_msg = event.message
        else:
            self.accepted_msg = event
            self.sent_msg = None

        self.last_text: Optional[str] = None

    async def send(self, text: str, **kwargs):
        if text == self.last_text:
            return self.sent_msg

        try:
            if not self.sent_msg:
                self.sent_msg = await self.accepted_msg.reply(text, **kwargs)
            else:
                if self.sent_msg.photo:
                    await self.sent_msg.edit_caption(caption=text, **kwargs)
                else:
                    await self.sent_msg.edit_text(text, **kwargs)

            self.last_text = text
            return self.sent_msg

        except TelegramBadRequest as e:
            if "message is not modified" in e.message.lower():
                return self.sent_msg
            logger.error(f"Критическая ошибка Telegram: {e}")
        except Exception as e:
            logger.error(f"Ошибка SmartResponse: {e}")