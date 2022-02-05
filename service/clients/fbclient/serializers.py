
from datetime import datetime

from pydantic import BaseModel


class NewsItem(BaseModel):
    uid: int
    title: str
    text: str
    time_created: datetime
    author: str


class Meeting(BaseModel):
    uid: int
    name: str
    fragment: str
    comment: str
    time: datetime
    intramural: int