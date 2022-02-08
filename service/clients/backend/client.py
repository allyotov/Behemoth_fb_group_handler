import logging
from pprint import pprint

import httpx
import orjson

from service.clients.backend.serializers import NewsItem


logger = logging.getLogger(__name__)


class BackClient:

    def __init__(self, url: str) -> None:
        self.url = url

    def send_newsitem(self, newsitem: NewsItem) -> None:
        try:
            r = httpx.post(
                url=f'{self.url}/api/news/',
                content=orjson.dumps(newsitem),
                headers={'content-type': 'application/json'},
            )
            r.raise_for_status()
            logger.debug('Очередная новость была отправлена в бекенд')
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            logger.debug('Не могу отправить новости из-за проблем с соединением.')
            logger.exception(exc)

    def get_newsitem(self, id):
        try:
            return httpx.get(url=f'{self.url}/api/news/', params={'id': id})
        except (httpx.ConnectError, httpx.RemoteProtocolError) as exc:
            logger.debug('Не могу получить сообщения из-за проблем с соединением.')
            logger.exception(exc)

    def edit_newsitem(self, newsitem: NewsItem):
        try:
            data=orjson.dumps(newsitem)
            pprint(data)
            resp = httpx.put(
                url=f'{self.url}/api/news/{newsitem.id}/',
                data=data,
                headers={'content-type': 'application/json'},
            )
            resp.raise_for_status()
            logger.debug('Очередная новость была изменена в бекенде')
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            logger.debug('Не могу отредактировать новость из-за проблем с соединением.')
            logger.exception(exc)

    def get_latest_newsitem(self):
        try:
            return httpx.get(url=f'{self.url}/api/news/', params={'latest': True})
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            logger.debug('Не могу получить сообщения из-за проблем с соединением.')
            logger.exception(exc)