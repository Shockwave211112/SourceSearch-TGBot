from datetime import datetime
from sqlalchemy import DateTime, func, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableList, MutableDict
from database.config import BaseModel
from enums.services import *
from typing import List

class ImageCache(BaseModel):
    __tablename__ = "image_cache"
    
    file_unique_id: Mapped[str] = mapped_column(String, primary_key=True)
    file_hash: Mapped[str] = mapped_column(String)
    results: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        insert_default=dict
    )
    searched_providers: Mapped[List[SearchProviders]] = mapped_column(
        MutableList.as_mutable(JSON),
        nullable=False,
        insert_default=list
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now())

    @property
    def has_results(self) -> bool:
        """
        Есть ли хотя бы один реальный результат поиска
        """
        if not self.results:
            return False
        return any(self.results.values())