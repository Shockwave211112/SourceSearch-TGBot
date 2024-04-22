from aiogram import Bot
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from saucenao_api import AIOSauceNao 
from saucenao_api.errors import *
from core.settings import settings
from urllib.parse import urlparse
from validators import url as urlValidator
import re, requests
from bs4 import BeautifulSoup

uselessHosts = ['i.pximg.net']
class PictureItem:
    def __init__(self, title = '', author = '', url = ''):
        self.title = title
        self.author = author
        self.url = url
        
    def __str__(self):
        return f'Title={self.title}\nAuthor={self.author}\nURL={self.url}'


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
            answer = "К сожалению, ничего не найдено.😞\nМожешь попробовать сам на сайтах \n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
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
    
def button_parser(picturesList: list, keyboard: InlineKeyboardBuilder, attachedUrls: list):
    for item in picturesList:
        parsedUrl = urlparse(item.url)
        if parsedUrl.hostname not in uselessHosts:
            attachedUrls.append(item.url)
            urlButton = InlineKeyboardButton(text=parsedUrl.hostname, url = item.url)
            keyboard.row(urlButton)
        
async def ascii2d_handler(photo_url: str):
    session = requests.session()
    ascii2dResults = []
    try:
        url = "https://ascii2d.net/"
        requestHeader = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
        }
        html = session.get(url, headers=requestHeader)
        authenticityToken = re.findall("<input type=\"hidden\" name=\"authenticity_token\" value=\"(.*?)\" />", html.text, re.S)[0]
        payloadData = {
            'utf8': "✓",
            'authenticity_token': authenticityToken
        }
        
        photo_file = requests.get(photo_url)
        files = {
            "file": 
            (
                "saucenao.jpg", photo_file.content, "image/png"
            )
        }
        url = "https://ascii2d.net/search/multi"
        postRequest = session.post(url=url, headers=requestHeader, data=payloadData, files=files)
        soup = BeautifulSoup(postRequest.text, 'html.parser')
        
        for item in soup.find_all('div', attrs={'class': 'row item-box'})[1:3]: 
            ascii2dList = item.find_all('a')
            title = str(ascii2dList[0].get_text())
            imageUrl = str(ascii2dList[0]["href"])
            author = str(ascii2dList[1].get_text())
            ascii2dResults.append(PictureItem(title, author, imageUrl))
            
        session.close()
        return ascii2dResults
    except:
        session.close()
        return False
    
async def saucenao_handler(photo_url: str):
    async with AIOSauceNao(settings.tokens.sauce_token) as aio:
        try:
            saucenaoResults = []
            results = await aio.from_url(photo_url)
            attachedUrls = []
            
            if results[0].similarity < 60:
                return False
            
            for item in results:
                if item.similarity >= 60:
                    if item.urls:
                        for url in item.urls:
                            if url not in attachedUrls:
                                attachedUrls.append(url)
                                saucenaoResults.append(PictureItem(item.title, item.author, url))
                    if 'source' in item.raw['data']:
                        if urlValidator(item.raw['data']['source']):
                            if item.raw['data']['source'] not in attachedUrls:
                                attachedUrls.append(item.raw['data']['source'])
                                saucenaoResults.append(PictureItem(item.title, item.author, item.raw['data']['source']))
                            
            return saucenaoResults
        except SauceNaoApiError:
            return False    