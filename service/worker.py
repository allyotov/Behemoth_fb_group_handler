import logging
import random
import time
from pprint import pprint

from service.clients import fbclient, backend 
from service.config import access_token, backend_url, time_delay

logger = logging.getLogger(__name__)


class Worker:

    def __init__(self) -> None:
        self.fb = fbclient.FbClient(access_token)
        self.backend = backend.BackClient(backend_url)
        self.delay = int(time_delay)

    def work(self) -> None:
        while True:
            try:
                fresh_newsitems = self.fb.get_newsitems()
            except Exception:
                raise

            pprint(fresh_newsitems)
            
            for newsitem in fresh_newsitems:
                saved_newsitem = self._convert_newsitem(newsitem)
                logger.debug('Забираем из бекенда новости по ид')
                news_from_backend = self.backend.get_newsitem(saved_newsitem.id).json()
                if len(news_from_backend) == 0:
                    self.backend.send_newsitem(saved_newsitem)
                else:
                    old_newsitem = news_from_backend[0]
                    if saved_newsitem.meeting_time != old_newsitem['meeting_time'] or \
                        saved_newsitem.updated_time != old_newsitem['updated_time'] or \
                        saved_newsitem.text != old_newsitem['text']:
                        logger.debug('Изменилась новость, будем менять в базе.')
                    else:
                        logger.debug('Новость не изменилась, оставляем как есть')
            break
            time.sleep(random.randrange(3, 10))
            logger.debug('I am waiting in 5 minutes to make a new query')
            time.sleep(self.delay)
            

    def _convert_newsitem(self, newsitem: fbclient.NewsItem) -> backend.NewsItem:
        return backend.NewsItem(
            id=newsitem.id,
            text=newsitem.text,
            updated_time=newsitem.updated_time,
            meeting_time=newsitem.meeting_time,
        )
