from aiogram.filters.callback_data import CallbackData
from typing import Optional
from schemas.source_item import SourceItem
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.formatting import Text, Bold
from utils.i18n import *

class ActionCallbackData(CallbackData, prefix="actionData"):
    action: str
    next_provider: str | None

def get_text(category: str, key: str, lang: str = "en", **kwargs):
    cat_dict = LOCALIZATION.get(category)
    lang_dict = cat_dict.get(lang, cat_dict.get("en", {}))
    text = lang_dict.get(key)

    if text is None:
        return f"[{category}:{key}]"

    return text.format(**kwargs)

def format_search_response(results: dict, next_provider: str = None, lang: str = "en") -> tuple[Text, Optional[InlineKeyboardMarkup]]:
    if not results:
        return Text(get_text("MESSAGES", "NOT_FOUND", lang)), None

    unique_items = {}
    for sublist in results.values():
        for item_data in sublist:
            item = SourceItem(**item_data)

            key = item.url
            if key not in unique_items:
                unique_items[key] = item

    all_items = sorted(unique_items.values(), key=lambda x: x.score, reverse=True)

    title = next((item.title for item in all_items if item.title), "Unknown")
    author = next((item.author for item in all_items if item.author), "Unknown")
    
    content = Text(
        Bold(get_text("LETTERS", "TITLE", lang)), title, "\n",
        Bold(get_text("LETTERS", "AUTHOR", lang)), author
    )
    
    builder = InlineKeyboardBuilder()
    seen_urls = set()

    for item in all_items:
        if item.url in seen_urls:
            continue
        
        builder.button(text=item.website, url=item.url)
        seen_urls.add(item.url)

    builder.adjust(2)

    if next_provider:
        builder.row(InlineKeyboardButton(
            text=get_text("BUTTONS", "SEARCH_MORE", lang),
            callback_data=ActionCallbackData(
                action="next",
                next_provider=next_provider
            ).pack()
        ))
    builder.row(InlineKeyboardButton(
        text=get_text("BUTTONS", "RETRY_PROVIDER", lang),
        callback_data=ActionCallbackData(
            action="retry_provider",
            next_provider=None
        ).pack()
    ))
    builder.row(InlineKeyboardButton(
        text=get_text("BUTTONS", "SEARCH_AGAIN", lang),
        callback_data=ActionCallbackData(
            action="search_again",
            next_provider=None
        ).pack()
    ))

    return content, builder.as_markup()