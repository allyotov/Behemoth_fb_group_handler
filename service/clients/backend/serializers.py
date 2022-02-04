from datetime import datetime

from dataclasses import dataclass


@dataclass
class Post:
    uid: int
    title: str
    text: str
    time_created: str
    author: str


@dataclass
class Meeting:
    uid: int
    name: str
    fragment: str
    comment: str
    time: str
    intramural: int