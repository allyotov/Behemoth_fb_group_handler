import logging

import httpx
import orjson

from service.clients.backend.serializers import Meeting, Post


logger = logging.getLogger(__name__)


class BackClient:

    def __init__(self, url: str) -> None:
        self.url = url

    def send_post(self, post: Post) -> None:
        try:
            httpx.post(
                url=f'{self.url}/api/news',
                content=orjson.dumps(post),
                headers={'content-type': 'application/json'},
            )
            logger.debug('new message has been sent to backend')
        except (httpx.ConnectError, httpx.RemoteProtocolError):
            logger.debug('Can\'t send message due to connection problem')
    
    def send_meeting(self, meeting: Meeting) -> None:
        try:
            httpx.post(
                url=f'{self.url}/api/meetings',
                content=orjson.dumps(meeting),
                headers={'content-type': 'application/json'},
            )
            logger.debug('new message has been sent to backend')
        except (httpx.ConnectError, httpx.RemoteProtocolError):
            logger.debug('Can\'t send message due to connection problem')

    # def get_group(self):
    #     try:
    #         response = httpx.get(f'{self.url}/api/group/')
    #         group = response.json()
    #         logger.debug('Group config has been recieved')
    #     except (httpx.ConnectError, httpx.RemoteProtocolError):
    #         logger.debug('Can\'t recieve group config due to connection problem')
    #         return None
    #     return group