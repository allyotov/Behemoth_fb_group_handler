import logging

import httpx
import orjson

from service.clients.backend.serializers import NewsItem


logger = logging.getLogger(__name__)


class BackClient:

    def __init__(self, url: str) -> None:
        self.url = url

    def send_newsitem(self, newsitem: NewsItem) -> None:
        try:
            httpx.post(
                url=f'{self.url}/api/news/',
                content=orjson.dumps(newsitem),
                headers={'content-type': 'application/json'},
            )
            logger.debug('Очередная новость была отправлена в бекенд')
        except (httpx.ConnectError, httpx.RemoteProtocolError) as exc:
            logger.debug('Не могу отправить сообщения из-за проблем с соединением.')
            logger.exception(exc)

    def get_newsitem(self, id):
        return httpx.get(url=f'{self.url}/api/news/', params={'id': id})