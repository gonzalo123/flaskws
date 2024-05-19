import logging
from typing import Dict, Any, Union

from flask import session
from flask_socketio import SocketIO
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Conf:
    def __init__(self, socketio=None):
        self._socketio = socketio

    @property
    def socketio(self):
        return self._socketio

    @socketio.setter
    def socketio(self, value):
        self._socketio = value


conf = Conf()


def emit_event(channel, body):
    conf.socketio.emit(channel, body)


class EmitWebsocketRequest(BaseModel):
    channel: str
    body: Union[Dict[str, Any], str]


def setup_ws(redis_host, redis_port=6379):
    conf.socketio = SocketIO(message_queue=f'redis://{redis_host}:{redis_port}')


def register_ws(
        app,
        redis_host,
        socketio_path='/ws/socket.io',
        redis_port=6379
):
    redis_url = f'redis://{redis_host}:{redis_port}' if redis_host else None
    conf.socketio = SocketIO(app, path=socketio_path, message_queue=redis_url)

    @conf.socketio.on('connect')
    def handle_connect():
        if not session.get("user"):
            raise ConnectionRefusedError('unauthorized!')
        logger.debug(f'Client connected: {session["user"]}')

    @conf.socketio.on('disconnect')
    def handle_disconnect():
        logger.debug('Client disconnected')

    return conf.socketio
