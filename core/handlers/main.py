from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.enums import ParseMode
from core.helpers import SearchCallbackData, ascii2d_keyboard
from core.searches import main_search
from core.lang import *
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(F.text == "/start", F.chat.type == "private")
async def get_start(message: Message, bot: Bot):
    await message.answer(HELLO_ANSWER)
    
@router.message(F.photo, F.chat.type == "private")
async def get_photo(message: Message, bot: Bot):
    file = await bot.get_file(message.photo[-1].file_id)
    search_results_keyboard, title, author = await main_search('saucenao', file.file_path)
    if search_results_keyboard:
        answer = FANDOM + title + "\n" + AUTHOR + author + "\n"
        
        search_results_keyboard.row(InlineKeyboardButton(
            text=ADDITIONAL_SEARCH_BTN, 
            callback_data=SearchCallbackData(
                action='additional_search',
                file_path=file.file_path).pack()
        ))
        await message.reply(answer, 
            reply_markup=search_results_keyboard.as_markup(), 
            parse_mode=ParseMode.HTML,
            disable_web_page_preview = True)
    else:
        await message.reply(SNAO_NOT_FOUND_ANSWER, 
            parse_mode=ParseMode.HTML,
            reply_markup=ascii2d_keyboard(file.file_path),
            resize_keyboard=True)

@router.callback_query(SearchCallbackData.filter(F.action == 'start_ascii2d_search'))    
async def ascii2d_search(callback: CallbackQuery, callback_data: SearchCallbackData):
    await callback.message.edit_text(PLS_WAIT_ANSWER,
        parse_mode=ParseMode.HTML, 
        disable_web_page_preview = True)
    
    search_results_keyboard, title, author = await main_search('ascii2d', callback_data.file_path)

    if search_results_keyboard:
        answer = TITLE + title + "\n" + AUTHOR + author + "\n"
        
        await callback.message.edit_text(answer,
            reply_markup=search_results_keyboard.as_markup(), 
            parse_mode=ParseMode.HTML,
            disable_web_page_preview = True)
    else:
        await callback.message.edit_text(NOT_FOUND_ANSWER,
            parse_mode=ParseMode.HTML, 
            disable_web_page_preview = True)
      
@router.callback_query(SearchCallbackData.filter(F.action == 'cancel_ascii2d_search'))    
async def ascii2d_search(callback: CallbackQuery):
    await callback.message.edit_text(NOT_FOUND_ANSWER,
        parse_mode=ParseMode.HTML, 
        disable_web_page_preview = True)
    
@router.message(F.chat.type == "private")         
async def get_anything(message: Message, bot: Bot):
    await message.answer(ERROR_ANSWER)

@router.callback_query(SearchCallbackData.filter(F.action == 'additional_search'))    
async def additional_search(callback: CallbackQuery, callback_data: SearchCallbackData):
    attached_urls = []
    callback.message.reply_markup.inline_keyboard[-1][0].text = PLS_WAIT_ANSWER
    await callback.message.edit_reply_markup(reply_markup=callback.message.reply_markup)
    
    callback.message.reply_markup.inline_keyboard.pop()
    attached_kb = callback.message.reply_markup.inline_keyboard
    for button in attached_kb:
        attached_urls.append(button[0].url)
    
    search_results_keyboard, title, author = await main_search('ascii2d', callback_data.file_path, attached_urls=attached_urls)
    if search_results_keyboard:    
        new_kb = InlineKeyboardBuilder()
        for button in attached_kb:
            new_kb.row(InlineKeyboardButton(text=button[0].text, url=button[0].url))
        for button in search_results_keyboard.as_markup().inline_keyboard:
            new_kb.row(InlineKeyboardButton(text=button[0].text, url=button[0].url))
            
        await callback.message.edit_reply_markup(reply_markup=new_kb.as_markup())
    else:
        await callback.message.edit_text(callback.message.text,
            reply_markup=callback.message.reply_markup,
            parse_mode=ParseMode.HTML, 
            disable_web_page_preview = True
        )