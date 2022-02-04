import logging

from service.worker import Worker

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.debug('fb group handler started')
    worker = Worker()
    worker.work()