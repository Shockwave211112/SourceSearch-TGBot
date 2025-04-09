from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiohttp import ClientSession

from urllib.parse import urlparse

from imagehash import average_hash
from PIL import Image
from io import BytesIO

useless_hosts = ['i.pximg.net', 'pbs.twimg.com', 'twimg.com']

class PictureItem:
    def __init__(self, title = '', author = '', url = ''):
        self.title = title
        self.author = author
        self.url = url
    def __str__(self):
        return f'Title={self.title}\nAuthor={self.author}\nURL={self.url}'
    
class SearchCallbackData(CallbackData, prefix="fileData"):
    action: str
    file_path: str

async def button_parser(picturesList: list, keyboard: InlineKeyboardBuilder, attachedUrls: list):
    for item in picturesList:
        parsedUrl = urlparse(item.url)
        if parsedUrl.hostname not in useless_hosts and item.url not in attachedUrls:
            attachedUrls.append(item.url)
            keyboard.row(InlineKeyboardButton(text=parsedUrl.hostname, url = item.url))
    
def ascii2d_keyboard(file_path: str):
    return InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Да", callback_data=SearchCallbackData(action='start_ascii2d_search', file_path=file_path).pack()), 
        InlineKeyboardButton(text="Нет", callback_data=SearchCallbackData(action='cancel_ascii2d_search', file_path=file_path).pack())
    ]
])
    
async def fetch_img_bytes(url: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            photo_bytes = await response.content.read()
    
    return photo_bytes

async def get_similarity(img1: bytes, img2: bytes):    
    image1Hash = average_hash(Image.open(BytesIO(img1)))
    image2Hash = average_hash(Image.open(BytesIO(img2)))
    
    distance = image1Hash - image2Hash
    similarity = (1 - (distance/64))*100
    
    return similarity