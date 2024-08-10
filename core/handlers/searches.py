from core.handlers.helpers import difference_images, PictureItem
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import ClientSession, FormData
from validators import url as urlValidator
from saucenao_api import AIOSauceNao
from core.settings import settings
from core.handlers.helpers import button_parser
from saucenao_api.errors import *
from bs4 import BeautifulSoup
from io import BytesIO
import re
import cfscrape

async def main_search(website: str, photo_url: str, attached_urls: list = []):
    fileUrl = "https://api.telegram.org/file/bot" + settings.tokens.bot_token + "/" + photo_url
    attachedUrls = attached_urls
    linksKeyboard = InlineKeyboardBuilder()
    if website == 'saucenao':
        searchResults = await saucenao_handler(fileUrl)
    if website == 'ascii2d':
        searchResults = await ascii2d_handler(fileUrl)

    if searchResults:
        await button_parser(searchResults, linksKeyboard, attachedUrls)

        for item in searchResults:
            if 'title' in locals() and 'author' in locals():
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

async def ascii2d_handler(photo_url: str):
    async with ClientSession() as session:
        try:
            ascii2dResults = []
            url = "https://ascii2d.net/"
            requestHeader = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
            }
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url).content.decode('UTF-8')
            authenticityToken = re.findall("<input type=\"hidden\" name=\"authenticity_token\" value=\"(.*?)\" />", response, re.S)[0]
            async with session.get(photo_url) as response:
                photo_file = await response.content.read()

            payloadData = {
                'utf8': '✓',
                'authenticity_token': authenticityToken
                }
            files = {
                'file': ('file.jpg', photo_file, 'image/jpg')
            }

            url = "https://ascii2d.net/search/multi"
            resultResponse = scraper.post(url, data=payloadData, files=files).content.decode('UTF-8')
            soup = BeautifulSoup(resultResponse, 'html.parser')
            for item in soup.find_all('div', attrs={'class': 'row item-box'})[:5]: 
                sourceDiv = item.find_all('div', attrs={'class': 'detail-box gray-link'})
                if sourceDiv[0].text in ['', '\n']:
                    continue
                sourceLinks = sourceDiv[0].find_all('a')
                title = sourceLinks[0].get_text()
                source = sourceLinks[0]["href"]
                if len(sourceLinks) > 1:
                    author = sourceLinks[1].get_text()
                else:
                    author = 'Unknown'
                img = 'https://ascii2d.net' + item.find_all('img')[0]['src']

                with scraper.get(img) as response:
                    img = response.content
                    if await difference_images(photo_file, img) == False:
                        ascii2dResults.append(PictureItem(title, author, source))
            
            if not ascii2dResults:
                return False
            else:
                return ascii2dResults
        except Exception as e:
            print(f'Error via ASCII2D search - {e}')
            return False
    
async def saucenao_handler(photo_url: str):
    async with ClientSession() as session:
        async with AIOSauceNao(settings.tokens.sauce_token) as aio:
            try:
                saucenaoResults = []
                async with session.get(photo_url) as response:
                    photo_file = await response.content.read()
                results = await aio.from_file(BytesIO(photo_file))
                attachedUrls = []
                
                if results[0].similarity < 65:
                    return False
                
                for item in results:
                    if item.similarity >= 65:
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
            except SauceNaoApiError as e:
                print(f'Error via SauceNao search - {e}')
                return False    
