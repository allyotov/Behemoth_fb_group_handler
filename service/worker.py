import logging
import random
import time
from pprint import pprint
from datetime import datetime, timedelta

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
                    old_newsitem_dict = news_from_backend[0]
                    old_newsitem = fbclient.NewsItem.parse_obj(old_newsitem_dict)
                    logger.debug(newsitem)
                    logger.debug(old_newsitem)
                    if self._if_newsitems_equal(newsitem, old_newsitem):
                        logger.debug('Новость не изменилась!!!')
                    else:
                        logger.debug('Новость изменилась')
                        self.backend.edit_newsitem(saved_newsitem)
                    # if saved_newsitem.meeting_time != old_newsitem['meeting_time'] or \
                    #     saved_newsitem.updated_time != old_newsitem['updated_time'] or \
                    #     saved_newsitem.text != old_newsitem['text']:
                    #     logger.debug('Изменилась новость, будем менять в базе.')
                    #     logger.debug(type(saved_newsitem.meeting_time))
                    #     logger.debug(type(old_newsitem['meeting_time']))
                    # else:
                    #     logger.debug('Новость не изменилась, оставляем как есть')
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

    def _if_newsitems_equal(self, newsitem: fbclient.NewsItem, old_newsitem: fbclient.NewsItem) -> bool:
        if newsitem.text != old_newsitem.text:
            logger.debug('Текст новости изменился.')
            return False
        if newsitem.updated_time - old_newsitem.updated_time != timedelta(seconds=0):
            logger.debug('Дата изменения обновилась')
            return False
        if (type(newsitem.meeting_time) is type(old_newsitem.meeting_time) is None):
            logger.debug('Новость по-прежнему не встреча')
        elif (type(newsitem.meeting_time) is type(old_newsitem.meeting_time) is datetime):
            if newsitem.meeting_time - old_newsitem.meeting_time != timedelta(seconds=0):
                logger.debug('Дата встречи изменилась')
                return False
        else:
            logger.debug('Новость стала/перестала быть встречей')
            return False
        return True
            
