from core.helpers import PictureItem
from core.settings import settings
from core.helpers import button_parser, fetch_img_bytes, get_similarity

from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

from validators import url as urlValidator

from PicImageSearch import SauceNAO, Ascii2D

async def main_search(website: str, photo_url: str, attached_urls: list = []):
    fileUrl = "https://api.telegram.org/file/bot" + settings.tokens.bot_token + "/" + photo_url
    attachedUrls = attached_urls
    linksKeyboard = InlineKeyboardBuilder() # Клавиатура с результатами
    
    if website == 'saucenao':
        searchResults = await saucenao_handler(fileUrl)
    if website == 'ascii2d':
        searchResults = await ascii2d_handler(fileUrl)
            
    if searchResults:
        await button_parser(searchResults, linksKeyboard, attachedUrls)

        for item in searchResults:
            if 'title' in locals() and 'author' in locals(): # Если тайтл и автор уже есть - выходим
                break
            if item.title != '':
                title = item.title.replace('&', '&amp').replace('<', '&lt').replace('>', '&gt')
            if item.author != '':
                author = item.author.replace('&', '&amp').replace('<', '&lt').replace('>', '&gt')
        
        if 'title' not in locals():
            title = 'Unknown'
        if 'author' not in locals():
            author = 'Unknown'

        return linksKeyboard, title, author
    else:
        return False, '404', '404'
    
async def run_blocking_io_in_thread(executor, func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))

async def saucenao_handler(photo_url: str):
        try:
            photo_bytes = await fetch_img_bytes(photo_url)
            
            engine = SauceNAO(api_key=settings.tokens.sauce_token)
            response = await engine.search(file=photo_bytes)
            apiResults = response.origin['results']
            
            if float(apiResults[0]['header']['similarity']) < 65:
                return False
            
            attachedUrls = []
            results = []
            
            for item in apiResults:
                header = item['header']
                data = item['data']
                if float(header['similarity']) >= 65:
                    # Основной источник
                    if data['source'] and urlValidator(data['source']):
                        if data['source'] not in attachedUrls:
                            attachedUrls.append(data['source'])
                            results.append(PictureItem(data['material'], data['creator'], data['source']))
                    # Доп ссылки
                    if data['ext_urls']:
                        for url in data['ext_urls']:
                            if url not in attachedUrls:
                                attachedUrls.append(url)
                                results.append(PictureItem(data['material'], data['creator'], url))
                                
            return results
        except Exception as e:
            print(f'Error via SauceNao search - {e}')
        

async def ascii2d_handler(photo_url: str):
    try:
        photo_bytes = await fetch_img_bytes(photo_url)
        
        engine = Ascii2D(base_url='https://ascii2d.obfs.dev/')
        response = await engine.search(file=photo_bytes)
        apiResults = response.raw
    
        attachedUrls = []
        results = []
        
        for item in apiResults:
            if item.url and urlValidator(item.url):
                if item.url not in attachedUrls:
                    item_bytes = await fetch_img_bytes(item.url)
                    similarity = await get_similarity(photo_bytes, item_bytes)
                    if similarity >= 65:
                        attachedUrls.append(item.url)
                        results.append(PictureItem(item.title, item.author, item.url))

        if not results:
            return False
        else:
            return results
        
    except Exception as e:
        print(f'Error via ASCII2D search - {e}')
        