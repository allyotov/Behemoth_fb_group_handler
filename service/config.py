import os
from datetime import datetime

access_token = os.environ['ACCESS_TOKEN']
group_id = os.environ['GROUP_ID']
backend_url = os.environ['BACKEND_URL']

time_delay = os.environ['TIME_DELAY']
default_check_start = datetime.strptime(os.environ['DEFAULT_CHECK_START'], '%Y-%m-%dT%H:%M:%S%z')

sentry_dsn = os.environ['SENTRY_DSN']