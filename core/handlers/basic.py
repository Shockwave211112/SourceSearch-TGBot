from aiogram import Bot
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.settings import settings
from core.handlers.helpers import button_parser
from core.handlers.searches import ascii2d_handler, saucenao_handler

async def get_start(message: Message, bot: Bot):
    await message.answer(f'Пришли картинку, я попробую найти оригинал и автора')
    
async def get_photo(message: Message, bot: Bot):
    file = await bot.get_file(message.photo[-1].file_id)
    fileUrl = "https://api.telegram.org/file/bot" + settings.tokens.bot_token + "/" + file.file_path
    answer = ''
    attachedUrls = []
    linksMarkup = InlineKeyboardBuilder()
    
    sauceNao = await saucenao_handler(fileUrl)
    if sauceNao:
        button_parser(sauceNao, linksMarkup, attachedUrls)
    else:
        ascii2d = await ascii2d_handler(fileUrl)
        if ascii2d:
            button_parser(ascii2d, linksMarkup, attachedUrls)
    
    if sauceNao == 0 and ascii2d == 0:
            answer = "К сожалению, ничего не найдено 😞\nМожешь попробовать сам на сайтах \n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
            await message.reply(answer, parse_mode=ParseMode.HTML, disable_web_page_preview = True)
    else:
        if sauceNao:
            for item in sauceNao:
                if item.title != '' and item.author != '':
                    title = item.title
                    author = item.author
                    break
        else:
            for item in ascii2d:
                if item.title != '' and item.author != '':
                    title = item.title
                    author = item.author
                    break
        
        answer = "<b>Название: </b>" + title + "\n<b>Автор: </b>" + author + "\n"
        answer += "\n<i>Если нету того, что нужно, попробуй вручную:</i>\n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
        await message.reply(answer, 
                            reply_markup=linksMarkup.as_markup(), 
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview = True)
            
async def get_anything(message: Message, bot: Bot):
    await message.answer(f'Такие сообщения я не понимаю.')
    
async def get_group_message(message: Message, bot: Bot):
    await message.answer(f'-')