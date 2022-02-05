from readline import append_history_file
from tokenize import group
from typing import Any, Tuple
import httpx
import logging

from service.clients.fbclient.serializers import Meeting, NewsItem
from service.config import group_id

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

FB_GROUPS_URL='https://graph.facebook.com/v12.0/{}/feed'

class FbClient:
    group_url = FB_GROUPS_URL.format(group_id)

    def __init__(self, token: str) -> None:
        self.token = token

    def get_posts(self) -> Tuple[list[NewsItem], list[Meeting]]:
        #since
        data: dict[str, str] = {
            'access_token': self.token,
        }

        response = httpx.get(self.group_url, params=data)
        response.raise_for_status()
        logger.debug('\n\n\n\n\n')
        # logger.debug(response.content)

        # data = response.json()
        
        # if 'response' not in data:
        #     logger.exception('Группа не сушествует! %s', data)
        #     raise Exception

        feed = response.json()
        news, meetings = self._process_feed(feed)
        return news, meetings
        # return [self._convert_posts(post, owner_id) for post in posts]
    def _process_feed(self, feed):
        updates = feed['data']
        news = []
        meetings = []
        for item in updates:
            if 'message' in item:
                if item['message'].startswith('Встреча'):
                    meetings.append({'message': item['message'], 'updated_time': item['updated_time']})
                else:
                    news.append({'message': item['message'], 'updated_time': item['updated_time']})
        return news, meetings
    
    def _convert_newsitem(self, post: dict[str, Any], owner_id: int) -> NewsItem:

        return NewsItem(
            uid=None,
            text=None,
        )

'''
class Post(BaseModel):
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
'''