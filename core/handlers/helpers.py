from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import urlparse
from imagehash import average_hash
from io import BytesIO
from PIL import Image

uselessHosts = ['i.pximg.net']

class PictureItem:
    def __init__(self, title = '', author = '', url = ''):
        self.title = title
        self.author = author
        self.url = url
        
    def __str__(self):
        return f'Title={self.title}\nAuthor={self.author}\nURL={self.url}'
    
class Ascii2dCallbackData(CallbackData, prefix="fileData"):
    action: str
    file_path: str

async def button_parser(picturesList: list, keyboard: InlineKeyboardBuilder, attachedUrls: list):
    for item in picturesList:
        parsedUrl = urlparse(item.url)
        if parsedUrl.hostname not in uselessHosts:
            attachedUrls.append(item.url)
            urlButton = InlineKeyboardButton(text=parsedUrl.hostname, url = item.url)
            keyboard.row(urlButton)
        
async def difference_images(img1, img2):
    image1Hash = average_hash(Image.open(BytesIO(img1)))
    image2Hash = average_hash(Image.open(BytesIO(img2)))
    
    difference = image1Hash - image2Hash
    if difference < 3:
        return False
    else:
        return True
    
def ascii2d_keyboard(file_path: str):
    return InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Да", callback_data=Ascii2dCallbackData(action='start_ascii2d_search', file_path=file_path).pack()), 
        InlineKeyboardButton(text="Нет", callback_data=Ascii2dCallbackData(action='cancel_ascii2d_search', file_path=file_path).pack())
    ]
])