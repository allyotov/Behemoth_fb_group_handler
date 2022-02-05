
from datetime import datetime

from pydantic import BaseModel


class NewsItem(BaseModel):
    id: str
    updated_time: datetime
    meeting_time: datetime = None
    text: str