from aiogram import Bot
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from saucenao_api import AIOSauceNao 
from saucenao_api.errors import *
from core.settings import settings
from urllib.parse import urlparse
from validators import url as urlValidator
import time

uselessHosts = ['i.pximg.net']
async def get_start(message: Message, bot: Bot):
    await message.answer(f'Пришли картинку, я попробую найти оригинал и автора')
    
async def get_photo(message: Message, bot: Bot):
    file_info = await bot.get_file(message.photo[-1].file_id)
    async with AIOSauceNao(settings.tokens.sauce_token) as aio: 
        try:
            results = await aio.from_url("https://api.telegram.org/file/bot" + settings.tokens.bot_token + "/" + file_info.file_path)
            answer = ''
            attachedUrls = []
            
            if results[0].similarity < 60:
                answer = "К сожалению, ничего не найдено.\nМожешь попробовать сам на сайтах \n<b>saucenao.com | yandex.ru/images/ | images.google.ru</b>"
                await message.reply(answer, parse_mode=ParseMode.HTML)
                return
            
            linksMarkup = InlineKeyboardBuilder()
            for item in results:
                if item.similarity >= 60:
                    if item.urls:
                        for url in item.urls:
                            if url not in attachedUrls:
                                button_parser(url, linksMarkup, attachedUrls)
                    if 'source' in item.raw['data']:
                        if urlValidator(item.raw['data']['source']):
                            if item.raw['data']['source'] not in attachedUrls:
                                button_parser(item.raw['data']['source'], linksMarkup, attachedUrls)
                            
            number_of_result = 0
            while results[number_of_result].author == None:
                number_of_result = number_of_result + 1
            answer = "<b>Название: </b>" + results[number_of_result].title + "\n<b>Автор: </b>" + results[number_of_result].author + "\n"
                            
            answer = answer + "\n<i>Если не нашлось сурса, попробуйте вручную на сайтах:</i>\n<b>saucenao.com | yandex.ru/images/ | images.google.ru</b>" 
            await message.reply(answer, 
                                reply_markup=linksMarkup.as_markup(), 
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview = True)
        except SauceNaoApiError:
            await message.reply('Слишком много запросов 😞\nНемного подождите и попробуйте ещё раз.')    
    
async def get_anything(message: Message, bot: Bot):
    await message.answer(f'Такие сообщения я не понимаю.')
    
async def get_group_message(message: Message, bot: Bot):
    await message.answer(f'-')
    
def button_parser(url: str, keyboard: InlineKeyboardBuilder, attachedUrls: list):
    parsedUrl = urlparse(url)
    if parsedUrl.hostname not in uselessHosts:
        attachedUrls.append(url)
        urlButton = InlineKeyboardButton(text=parsedUrl.hostname, url = url)
        keyboard.row(urlButton)