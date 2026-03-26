from datetime import datetime
from sqlalchemy import BigInteger, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column
from database.config import BaseModel
from core.config import settings

class User(BaseModel):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    language_code: Mapped[str] = mapped_column(String(5), default="en")
    daily_limit: Mapped[int] = mapped_column(default=settings.DAILY_LIMIT)
    requests_today: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_request: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def check_requests(self) -> bool:
        """Проверяет, не наступил ли новый день, и обновляет лимиты"""
        now = datetime.now()
        
        if self.last_request.date() < now.date():
            self.requests_today = 0
            
        return self.requests_today < self.daily_limit