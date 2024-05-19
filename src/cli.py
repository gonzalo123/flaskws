from lib.ws import emit_event, setup_ws
from settings import REDIS_HOST

setup_ws(redis_host=REDIS_HOST)
emit_event('message', 'Hi')
