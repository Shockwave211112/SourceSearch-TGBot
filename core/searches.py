from core.helpers import PictureItem
from core.settings import settings
from core.helpers import button_parser, fetch_img_bytes, get_similarity

from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

from validators import url as urlValidator

from PicImageSearch import SauceNAO, Ascii2D

async def main_search(website: str, photo_url: str, attached_urls: list = []):
    file_url = "https://api.telegram.org/file/bot" + settings.tokens.bot_token + "/" + photo_url
    links_keyboard = InlineKeyboardBuilder() # Клавиатура с результатами
    
    if website == 'saucenao':
        search_results = await saucenao_handler(file_url)
    if website == 'ascii2d':
        search_results = await ascii2d_handler(file_url)
            
    if search_results:
        await button_parser(search_results, links_keyboard, attached_urls)

        for item in search_results:
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

        return links_keyboard, title, author
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
            api_results = response.origin['results']
            
            if float(api_results[0]['header']['similarity']) < 65:
                return False
            
            attached_urls = []
            results = []
            
            for item in api_results:
                header = item['header']
                data = item['data']
                source = data.get('source')
                ext_urls = data.get('ext_urls')
                if float(header['similarity']) >= 65:
                    # Основной источник
                    if source and urlValidator(source):
                        if source not in attached_urls:
                            author = data.get('creator') or data.get('member_name') or 'Unknown'
                            title = data.get('title') or data.get('material') or 'Unknown'
                            attached_urls.append(source)
                            results.append(PictureItem(title, author, source))
                    # Доп ссылки
                    if ext_urls:
                        for url in ext_urls:
                            if url not in attached_urls:
                                author = data.get('creator') or data.get('member_name') or 'Unknown'
                                title = data.get('title') or data.get('material') or 'Unknown'
                                attached_urls.append(url)
                                results.append(PictureItem(title, author, url))
                                
            return results
        except Exception as e:
            print(f'Error via SauceNao search - {e}')
        

async def ascii2d_handler(photo_url: str):
    try:
        photo_bytes = await fetch_img_bytes(photo_url)
        
        engine = Ascii2D(base_url='https://ascii2d.obfs.dev/')
        response = await engine.search(file=photo_bytes)
        api_results = response.raw
    
        attached_urls = []
        results = []
        
        for item in api_results:
            if item.url and urlValidator(item.url):
                if item.url not in attached_urls:
                    item_bytes = await fetch_img_bytes(item.thumbnail)
                    similarity = await get_similarity(photo_bytes, item_bytes)
                    if similarity >= 90:
                        attached_urls.append(item.url)
                        results.append(PictureItem(item.title, item.author, item.url))

        if not results:
            return False
        else:
            return results
        
    except Exception as e:
        print(f'Error via ASCII2D search - {e}')
        