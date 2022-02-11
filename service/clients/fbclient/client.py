from datetime import datetime
from pytz import timezone
from typing import Any
import httpx
import logging

from service.clients.fbclient.serializers import NewsItem
from service.config import group_id

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

FB_GROUPS_URL='https://graph.facebook.com/v12.0/{}/feed'

MONTHS = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',  
    'июля': '07',
    'августа': '08', 
    'сентября': '09', 
    'октября': '10',
    'ноября': '11',
    'декабря': '12',
}

MOSCOW_TZ = timezone('Europe/Moscow')
class FbClient:
    group_url = FB_GROUPS_URL.format(group_id)

    def __init__(self, token: str) -> None:
        self.token = token

    def get_newsitems(self, latest_prev_news_date: str) -> list[NewsItem]:

        data: dict[str, str] = {
            'access_token': self.token,
        }
        if latest_prev_news_date:
            data['since'] = latest_prev_news_date

        try:
            response = httpx.get(self.group_url, params=data)
            response.raise_for_status()
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            logger.debug('Не могу получить сообщения из соцсети из-за проблем с соединением.')
            logger.exception(exc)
            raise PermissionError('Can\'t connect to the social network.')

        feed = response.json()
        news = self._process_feed(feed)

        return news

    def _process_feed(self, feed):
        updates = feed['data']
        news = []
        for item in updates:
            if 'message' in item:
                meeting_datetime, text = self._process_message(item['message'])
                news.append({
                    'id': item['id'],
                    'updated_time': item['updated_time'],
                    'meeting_time': meeting_datetime,
                    'text': text
                })
        return [self._convert_newsitem(newsitem) for newsitem in news]

    def _process_message(self, msg: str) -> datetime or None:
        if not msg.startswith('Встреча'):
            return None, msg
        msg_lines = msg.split('\n')
        first_line = msg_lines[0]
        parts = first_line.split()
        if len(parts) != 3:
            return None, msg
        _, date, time = parts
        if len(date) == 9:
            date = '0' + date
        datetime_str = ' '.join([date, time])
        try:
            dt = datetime.strptime(datetime_str, '%d.%m.%Y %H:%M')
            loc_dt = MOSCOW_TZ.localize(dt, is_dst=True)

            msg_lines.pop(0)

            return loc_dt, '\n'.join(msg_lines)
        except ValueError as err:
            logger.exception(err)
            return None, msg
        

    def _convert_newsitem(self, news_item: dict[str, Any]) -> NewsItem:

        return NewsItem(
            id=news_item['id'],
            updated_time=news_item['updated_time'],
            meeting_time=news_item['meeting_time'],
            text=news_item['text']
        )
