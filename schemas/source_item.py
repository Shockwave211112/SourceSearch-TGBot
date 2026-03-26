from pydantic import BaseModel
from typing import Any

class SourceItem(BaseModel):
    website: str  # 'danbooru', 'x', 'e-hen', 'pixiv', etc
    url: str
    author: str | None = None
    title: str | None = None
    score: float
    ext_data: dict[str, Any] = {}