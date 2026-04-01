from urllib.parse import urlparse

from utils.helpers import check_useless_hostname
from .base_search import BaseSearchProvider
from schemas.source_item import SourceItem
from core.config import settings

class DanbooruProvider(BaseSearchProvider):
    async def search(self, image_bytes: bytes) -> list[SourceItem]:
        url = f"https://{settings.DANBOORU_DOMAIN}/iqdb_queries.json"
        files = {"search[file]": ("image.jpg", image_bytes, "image/jpeg")}
        
        response = await self._make_request(
            "POST", url, 
            files=files, 
            auth=(settings.DANBOORU_LOGIN, settings.DANBOORU_API_KEY.get_secret_value())
        )
        
        if not response:
            return []

        results = response.json()
        return self._parse_results(results)

    def _parse_results(self, data: list) -> list[SourceItem]:
        source_list = []
        for item in data:
            post = item.get("post")
            if not post or item.get("score", 0) < 65:
                continue

            if post.get('pixiv_id'):
                source_list.append(SourceItem(
                    website="pixiv.net",
                    url=f"https://pixiv.net/artworks/{post.get('pixiv_id')}",
                    title=f"{post.get('tag_string_copyright', '')} {post.get('tag_string_character', '')}".strip(),
                    author=post.get("tag_string_artist"),
                    score=round(item.get("score"), 2)
                ))

            source_list.append(SourceItem(
                website=settings.DANBOORU_DOMAIN,
                url=f"https://{settings.DANBOORU_DOMAIN}/post/show/{post.get('id')}",
                title=f"{post.get('tag_string_copyright', '')} {post.get('tag_string_character', '')}".strip(),
                author=post.get("tag_string_artist"),
                score=round(item.get("score"), 2),
            ))

            hostname = urlparse(post.get("source", "")).hostname
            if not check_useless_hostname(hostname):
                source_list.append(SourceItem(
                    website=hostname,
                    url=post.get("source"),
                    title=f"{post.get('tag_string_copyright', '')} {post.get('tag_string_character', '')}".strip(),
                    author=post.get("tag_string_artist"),
                    score=round(item.get("score"), 2)
                ))
        return source_list