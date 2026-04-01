from urllib.parse import urlparse
from PicImageSearch import SauceNAO, Network
from core.config import settings
from schemas.source_item import SourceItem
from services.base_search import BaseSearchProvider
from utils.helpers import check_useless_hostname

class SauceNAOProvider(BaseSearchProvider):
    async def search(self, image_bytes: bytes) -> list[SourceItem]:
        async with Network(headers=self.headers) as client:
            saucenao = SauceNAO(
                client=client,
                api_key=settings.SAUCENAO_API_KEY.get_secret_value()
            )
            response = await saucenao.search(file=image_bytes)
                
            if not response or not response.raw:
                return []

            return self._parse_results(response.raw)
        
    def _parse_results(self, data: list) -> list[SourceItem]:
        source_list = []
        for item in data:
            if item.similarity < 65:
                continue

            hostname = urlparse(item.url).hostname
            if not check_useless_hostname(hostname):
                source_list.append(SourceItem(
                    website=hostname,
                    url=item.url,
                    title=item.title,
                    author=item.author,
                    score=item.similarity
                ))

            for extra in item.ext_urls:
                hostname = urlparse(extra).hostname
                if not check_useless_hostname(hostname):
                    source_list.append(SourceItem(
                        website=hostname,
                        url=extra,
                        title=item.title,
                        author=item.author,
                        score=item.similarity
            ))   
        return source_list