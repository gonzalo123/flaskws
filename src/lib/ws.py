import logging

from flask import session
from flask_socketio import ConnectionRefusedError
from flask_socketio import SocketIO

from lib.config import conf

logger = logging.getLogger(__name__)


def emit_event(channel, body):
    conf.socketio.emit(channel, body)


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

    @conf.socketio.on_error_default
    def default_error_handler(e):
        logger.error(f"An error occurred: {e}")

    return conf.socketio
