from typing import Any
import httpx
import logging

from service.clients.fbclient.serializers import Post, Comment

logger = logging.getLogger(__name__)


class FbClient:
    groups_url = ''
    v_api = '10'

    def __init__(self, token: str, chunk: int) -> None:
        self.token = token
        self.chunk = chunk

    def get_posts(self, owner_id: int, offset: int) -> list[Post]:
        data: dict[str, str] = {
            'owner_id': str(owner_id),
            'access_token': self.token,
            'offset': str(offset),
            'v': self.v_api,
        }

        response = httpx.get(self.posts_url, params=data)
        data = response.json()
        response.raise_for_status()
        if 'response' not in data:
            logger.exception('Группа не сушествует! %s', data)
            raise Exception

        posts = response.json()['response']['items']
        return [self._convert_posts(post, owner_id) for post in posts]

    def _convert_posts(self, post: dict[str, Any], owner_id: int) -> Post:

        return Post(
            uid=,
            text=,
        )