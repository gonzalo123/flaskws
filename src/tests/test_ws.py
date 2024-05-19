from unittest.mock import Mock

import pytest

from lib.ws import conf, emit_event, Conf

mock_socketio = Mock()


def test_emit_event():
    conf.socketio = mock_socketio
    emit_event('test_channel', 'test_body')

    mock_socketio.emit.assert_called_once_with('test_channel', 'test_body')


def test_emit_event_exception_handling():
    conf.socketio = Mock()
    conf.socketio.emit.side_effect = Exception('Test exception')

    with pytest.raises(Exception):
        emit_event('test_channel', 'test_body')


def test_conf_initialization():
    conf = Conf()
    assert conf.socketio is None


def test_conf_socketio_assignment():
    conf = Conf()
    mock_socketio = object()

    conf.socketio = mock_socketio

    assert conf.socketio is mock_socketio


def test_conf_socketio_assignment_multiple_times():
    conf = Conf()
    mock_socketio1 = object()
    mock_socketio2 = object()

    conf.socketio = mock_socketio1
    assert conf.socketio is mock_socketio1

    conf.socketio = mock_socketio2
    assert conf.socketio is mock_socketio2
