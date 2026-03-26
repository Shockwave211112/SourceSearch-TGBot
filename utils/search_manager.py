from datetime import datetime
import io
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.image_cache import ImageCache
from database.models.user import User
from enums.services import SearchProviders
from services.danbooru import DanbooruProvider
from services.saucenao import SauceNAOProvider
import imagehash
from PIL import Image

class InsufficientLimitsError(Exception):
    """Исключение: у пользователя закончились попытки поиска"""
    pass

class SearchManager:
    def __init__(self, database_session: AsyncSession, user: User):
        self.database_session = database_session
        self.user = user

    SEARCH_ORDER = [
        SearchProviders.DANBOORU,
        SearchProviders.SAUCENAO,
    ]
    
    def _get_provider_instance(self, provider_type: SearchProviders):
        """Фабрика провайдеров"""
        if provider_type == SearchProviders.DANBOORU:
            return DanbooruProvider()
        if provider_type == SearchProviders.SAUCENAO:
            return SauceNAOProvider()
        raise ValueError(f"Unknown provider: {provider_type}")

    async def get_cache(self, file_unique_id: str) -> Optional[ImageCache]:
        """
        Просто берем то, что есть в базе
        """
        return await self.database_session.get(ImageCache, file_unique_id)

    async def reset_cache(self, file_unique_id: str):
        """
        Сброс поиска
        """
        cache = await self.get_cache(file_unique_id)
        if cache:
            cache.searched_providers = []
            cache.results = {}
            await self.database_session.commit()

    class InsufficientLimitsError(Exception):
        """Исключение: у пользователя закончились попытки поиска"""
        pass

    def _get_providers_queue(self, searched_providers: list) -> List[SearchProviders]:
        """
        Получить доступную для картинки очередь провайдеров
        """
        return [provider for provider in self.SEARCH_ORDER if provider not in searched_providers]

    def _get_next_provider_name(self, searched_providers: list) -> Optional[str]:
        """
        Вспомогательный метод для определения имени следующего провайдера
        """
        queue = self._get_providers_queue(searched_providers)
        return queue[0].value if queue else None

    async def get_results_or_none(self, file_unique_id: str) -> tuple[dict, str | None] | tuple[None, None]:
        """
        Проверяет кэш. Если результаты есть — возвращает их сразу.
        """
        cache = await self.get_cache(file_unique_id)
        if cache and cache.results:
            return cache.results, self._get_next_provider_name(cache.searched_providers)
        return None, None

    async def do_all_search(
        self,
        file_unique_id: str, 
        image_bytes: bytes,
        force: bool = False
    ) -> tuple[dict, str | None]:
        """
        Ищем пока не найдем или возвращаем из кэша
        """
        cache = await self.get_cache(file_unique_id)
        if not cache:
            with Image.open(io.BytesIO(image_bytes)) as img:
                cache = ImageCache(
                    file_unique_id=file_unique_id,
                    file_hash=str(imagehash.average_hash(img)),
                    searched_providers=[], 
                    results={}
                )
                self.database_session.add(cache)

        queue = self._get_providers_queue(cache.searched_providers)

        # Ищем пока не найдем или пока не закончатся провайдеры
        while (not cache.has_results or force) and queue:
            force = False

            if not self.user.check_requests():
                raise InsufficientLimitsError("Daily limit reached")

            current_provider_enum = queue.pop(0)

            provider = self._get_provider_instance(current_provider_enum)
            results = await provider.search(image_bytes)

            # Обновляем БД и лимиты
            cache.searched_providers = list(cache.searched_providers) + [current_provider_enum]
            if results:
                cache.results[current_provider_enum.value] = [r.model_dump() for r in results]
            else:
                cache.results[current_provider_enum.value] = []

            self.user.requests_today += 1
            self.user.last_request = datetime.now()
            await self.database_session.commit()

        return cache.results, self._get_next_provider_name(cache.searched_providers)

    async def retry_last_provider(self, file_unique_id: str):
        """
        Прогон по последнему провайдеру
        """
        cache = await self.get_cache(file_unique_id)
        if cache and cache.searched_providers:
            new_providers = list(cache.searched_providers)
            last_provider = new_providers.pop()
            del cache.results[last_provider]
            cache.searched_providers = new_providers
            await self.database_session.commit()