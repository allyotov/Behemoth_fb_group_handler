import logging
import random
import time

from service.clients import backend, fbclient
from service.config import access_token, backend_url, time_delay

logger = logging.getLogger(__name__)


class Worker:

    def __init__(self) -> None:
        self.fb = fb.FbClient(access_token, chunk=1)
        self.backend = backend.BackClient(backend_url)
        self.delay = int(time_delay)

    def work(self) -> None:
        while True:
            group = self.backend.get_group()
            if not group:
                logger.debug(f'Can\'t receive a config from backend {backend_url}.\
                             I will try once again in 5 minutes')
                time.sleep(self.delay)
                continue

            owner_id = group['id']
            last_post_date = group['last_post_date']
            try:
                new_post = self.fb.get_posts(owner_id, offset=0)[0]
            except Exception:
                pass

            if new_post.date <= last_post_date:
                logger.debug(f"There are no new messages in group {owner_id}")
                continue
            saved_post = self._convert_post(new_post)
            self.backend.send_post(saved_post)
            time.sleep(random.randrange(3, 10))

            logger.debug('I am waiting in 5 minutes to make a new query')
            time.sleep(self.delay)

    def _convert_post(self, post: fbclient.Post) -> backend.Post:
        return backend.Post(
            uid=post.uid,
            created=post.created,
            author=post.author_id,
            text=post.text,
        )
