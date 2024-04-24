from core.handlers.helpers import difference_images, PictureItem
from validators import url as urlValidator
from saucenao_api import AIOSauceNao 
from core.settings import settings
from saucenao_api.errors import *
from bs4 import BeautifulSoup
from io import BytesIO
import re, requests

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
                "temp.jpg", photo_file.content, "image/jpg"
            )
        }
        url = "https://ascii2d.net/search/multi"
        postRequest = session.post(url=url, headers=requestHeader, data=payloadData, files=files)
        soup = BeautifulSoup(postRequest.text, 'html.parser')
        
        for item in soup.find_all('div', attrs={'class': 'row item-box'})[:5]: 
            sourceDiv = item.find_all('div', attrs={'class': 'detail-box gray-link'})
            if sourceDiv[0].text in ['', '\n']:
                continue
            sourceLinks = sourceDiv[0].find_all('a')
            title = sourceLinks[0].get_text()
            source = sourceLinks[0]["href"]
            author = sourceLinks[1].get_text()
            img = 'https://ascii2d.net' + item.find_all('img')[0]['src']
            if difference_images(photo_file.content, requests.get(img).content) == False:
                ascii2dResults.append(PictureItem(title, author, source))
            
        session.close()
        if not ascii2dResults:
            return False
        else:
            return ascii2dResults
    except:
        session.close()
        return False
    
async def saucenao_handler(photo_url: str):
    async with AIOSauceNao(settings.tokens.sauce_token) as aio:
        try:
            saucenaoResults = []
            photo_file = requests.get(photo_url)
            results = await aio.from_file(BytesIO(photo_file.content))
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