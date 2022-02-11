import logging
import random
import time
from datetime import datetime, timedelta

import pytz
import sentry_sdk

from service.clients import fbclient, backend 
from service.config import access_token, backend_url, time_delay, default_check_start, sentry_dsn


logger = logging.getLogger(__name__)


class Worker:

    def __init__(self) -> None:
        sentry_sdk.init(
            sentry_dsn,
            traces_sample_rate=1.0
        )

        self.fb = fbclient.FbClient(access_token)
        self.backend = backend.BackClient(backend_url)
        self.delay = int(time_delay)
        self.fb_error_newsitem_sent = False

    def work(self) -> None:
        while True:
            try:
                fresh_newsitems = self.fb.get_newsitems(latest_prev_news_date=self._latest_newsitem_date())
                logger.debug('Количество новых записей: %s' % len(fresh_newsitems))
                if not fresh_newsitems:
                    logger.debug('Cвежих новостей нет. Жду перед повторной проверкой группы соцсети.')
                    time.sleep(self.delay + random.randrange(3, 10))
                    continue
            except ConnectionError as exc:
                self._wait_to_request_backend(exc)
                continue
            except PermissionError as exc:
                self._send_fb_no_reply_newsitem(exc)
                continue
            
            self.fb_error_newsitem_sent = False
            for newsitem in fresh_newsitems:
                saved_newsitem = self._convert_newsitem(newsitem)

                logger.debug('Забираем из бекенда новости по ид')
                
                while True: 
                    try:
                        news_from_backend = self.backend.get_newsitem(saved_newsitem.id).json()
                        break
                    except ConnectionError as exc:
                        self._wait_to_request_backend(exc)
                
                if len(news_from_backend) == 0:
                    logger.debug('Новости с таким id в бекенде нет. Отправляем её в бекенд.')
                    while True: 
                        try:
                            self.backend.send_newsitem(saved_newsitem)
                            break
                        except ConnectionError as exc:
                            self._wait_to_request_backend(exc)
                else:
                    old_newsitem_dict = news_from_backend[0]
                    old_newsitem = fbclient.NewsItem.parse_obj(old_newsitem_dict)
                    logger.debug(newsitem)
                    logger.debug(old_newsitem)
                    if self._if_newsitems_equal(newsitem, old_newsitem):
                        logger.debug('Новость не изменилась!!!')
                    else:
                        logger.debug('Новость изменилась')
                        while True: 
                            try:
                                self.backend.edit_newsitem(saved_newsitem)
                                break
                            except ConnectionError as exc:
                                self._wait_to_request_backend(exc)

            logger.debug('Жду перед повторной проверкой группы соцсети.')
            time.sleep(self.delay + random.randrange(3, 10))
            

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
        if (newsitem.meeting_time is old_newsitem.meeting_time is None):
            logger.debug('Новость по-прежнему не встреча')
        elif (type(newsitem.meeting_time) is type(old_newsitem.meeting_time) is datetime):
            if newsitem.meeting_time - old_newsitem.meeting_time != timedelta(seconds=0):
                logger.debug('Дата встречи изменилась')
                return False
        else:
            logger.debug('Новость стала/перестала быть встречей')
            return False
        return True

    def _latest_newsitem_date(self):
        logger.debug('Latest newsitem date')
        news_from_backend = self.backend.get_latest_newsitem().json()
        if len(news_from_backend) == 0:
            logger.debug('Empty newsitem list')
            logger.debug('БД бекенда пока пуста. Берем дефолтную дату начала проверки')
            logger.debug(default_check_start)
            return default_check_start
        else:
            old_newsitem_dict = news_from_backend[0]
            latest_item = fbclient.NewsItem.parse_obj(old_newsitem_dict)
            latest_update = latest_item.updated_time
            logger.debug(latest_update)
            latest_update_utc = latest_update.astimezone(pytz.utc)
            logger.debug(latest_update_utc)
            logger.debug('Успешно получили дату сохранённой новости!')

            return latest_update_utc.strftime("%Y-%m-%dT%H:%M:%S+0000")

    def _wait_to_request_backend(self, exc):
        logger.exception(exc)
        logger.debug('Не могу получить ответ от бекэнда, жду и повторяю попытку запроса.')
        time.sleep(self.delay * 2)
        logger.debug('Повторяю попытку запроса к бекэнду.')

    def _send_fb_no_reply_newsitem(self, exc):
        if self.fb_error_newsitem_sent:
            return 
        logger.exception(exc)
        fb_no_reply_newsitem = None
        self.fb_error_newsitem_sent = True
        while True: 
            try:
                self.backend.send_newsitem(fb_no_reply_newsitem)
                break
            except ConnectionError as exc:
                self._wait_to_request_backend(exc)