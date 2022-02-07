from datetime import datetime

from dataclasses import dataclass


@dataclass
class NewsItem:
    id: str
    text: str
    updated_time: datetime
    meeting_time: datetime = None