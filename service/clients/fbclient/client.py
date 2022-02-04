from tokenize import group
from typing import Any
import httpx
import logging

from service.clients.fbclient.serializers import Post, Meeting
from service.config import group_id

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

FB_GROUPS_URL='https://graph.facebook.com/v12.0/{}/feed'

class FbClient:
    group_url = FB_GROUPS_URL.format(group_id)

    def __init__(self, token: str) -> None:
        self.token = token

    def get_posts(self) -> list[Post]:
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
        return feed
        # return [self._convert_posts(post, owner_id) for post in posts]

    def _convert_posts(self, post: dict[str, Any], owner_id: int) -> Post:

        return Post(
            uid=None,
            text=None,
        )