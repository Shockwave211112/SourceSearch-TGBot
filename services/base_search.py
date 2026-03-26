import logging
import httpx
from abc import ABC, abstractmethod
from typing import Optional, List, Any
from schemas.source_item import SourceItem
from core.config import settings

logger = logging.getLogger(__name__)

class BaseSearchProvider(ABC):
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            "User-Agent": f"{settings.USER_AGENT}"
        }

    @abstractmethod
    async def search(self, image_bytes: bytes) -> Optional[List[SourceItem]]:
        """
        Главный метод, который должен реализовать каждый провайдер.
        Возвращает список результатов или None, если сервис упал.
        """
        pass

    async def _make_request(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> Optional[httpx.Response]:
        async with httpx.AsyncClient(
            timeout=self.timeout, 
            headers=self.headers,
            follow_redirects=True
        ) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                logger.error(f"Ошибка статуса {e.response.status_code} для {url}")
            except httpx.RequestError as e:
                logger.error(f"Ошибка сети при запросе к {url}: {e}")
            except Exception as e:
                logger.exception(f"Непредвиденная ошибка в провайдере: {e}")
            
            return None
        
    @abstractmethod
    def _parse_results(self, data: Any) -> list[SourceItem]:
        """Каждый дочерний класс обязан реализовать этот метод по-своему"""
        pass