from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from urllib.parse import urlparse
from imagehash import average_hash
from io import BytesIO
from PIL import Image
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

uselessHosts = ['i.pximg.net']

class PictureItem:
    def __init__(self, title = '', author = '', url = ''):
        self.title = title
        self.author = author
        self.url = url
        
    def __str__(self):
        return f'Title={self.title}\nAuthor={self.author}\nURL={self.url}'

def button_parser(picturesList: list, keyboard: InlineKeyboardBuilder, attachedUrls: list):
    for item in picturesList:
        parsedUrl = urlparse(item.url)
        if parsedUrl.hostname not in uselessHosts:
            attachedUrls.append(item.url)
            urlButton = InlineKeyboardButton(text=parsedUrl.hostname, url = item.url)
            keyboard.row(urlButton)
        
def difference_images(img1, img2):
    image1Hash = average_hash(Image.open(BytesIO(img1)))
    image2Hash = average_hash(Image.open(BytesIO(img2)))
    
    difference = image1Hash - image2Hash
    if difference <= 5:
        return False
    else:
        return True

class Ascii2dQuestion(StatesGroup):
    wait_ascii2d = State()

yes_no_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
], resize_keyboard=True)

async def clear_cache(state: FSMContext):
    await state.set_state(None)
    await state.update_data(message_for_answer = '', file_url = '')