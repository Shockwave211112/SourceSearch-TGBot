import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from io import BytesIO
from utils.answer_utils import *
from utils.search_manager import InsufficientLimitsError, SearchManager

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "/start", F.chat.type == "private")
async def get_start(message: Message, lang: str):
    await message.answer(get_text("MESSAGES", "WELCOME", lang))

@router.message(F.photo, F.chat.type == "private", F.media_group_id == None)
async def handle_search(
        message: Message,
        session: AsyncSession,
        user: User,
        bot: Bot,
        lang: str
):
    file = message.photo[-1]
    manager = SearchManager(session, user)

    results, next_provider = await manager.get_results_or_none(file.file_unique_id)

    if results is None:
        try:
            buffer = BytesIO()
            await bot.download(file, destination=buffer)

            results, next_provider = await manager.do_all_search(
                file_unique_id=file.file_unique_id,
                image_bytes=buffer.getvalue()
            )
        except InsufficientLimitsError:
            return await message.reply(get_text("MESSAGES", "LIMITS_ERROR", lang), show_alert=True)

    text, reply_markup = format_search_response(results, next_provider, lang)
    
    await message.reply(
        **text.as_kwargs(),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

@router.callback_query(ActionCallbackData.filter())
async def handle_action(
        callback: CallbackQuery,
        callback_data: ActionCallbackData,
        session: AsyncSession,
        user: User,
        bot: Bot,
        lang: str
):
    """
    Обработка доп. кнопок
    """
    manager = SearchManager(session, user)
    file = callback.message.reply_to_message.photo[-1]
    file_unique_id = file.file_unique_id

    is_force = False
    if callback_data.action == "search_again":
        await manager.reset_cache(file_unique_id)
    elif callback_data.action == "retry_provider":
        is_force = True
        await manager.retry_last_provider(file_unique_id)
    elif callback_data.action == "next":
        is_force = True

    try:
        await callback.message.edit_text(
            get_text("MESSAGES", "PLS_WAIT", lang),
            reply_markup=None,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при повторном поиске - {e}")

    try:
        buffer = BytesIO()
        await bot.download(file, destination=buffer)

        results, next_provider = await manager.do_all_search(
            file_unique_id=file_unique_id,
            image_bytes=buffer.getvalue(),
            force=is_force
        )

        text, reply_markup = format_search_response(results, next_provider, lang)
        await callback.message.edit_text(
            **text.as_kwargs(),
            reply_markup=reply_markup
        )

    except InsufficientLimitsError:
        await callback.answer(get_text("MESSAGES", "LIMITS_ERROR", lang), show_alert=True)

    await callback.answer()

@router.message(F.photo, F.chat.type == "private", F.media_group_id != None)
async def get_anything(message: Message, lang: str):
    await message.answer(get_text("MESSAGES", "ALBUM_ERROR", lang))

@router.message(F.chat.type == "private")
async def get_anything(message: Message, lang: str):
    await message.answer(get_text("MESSAGES", "UNKNOWN", lang))