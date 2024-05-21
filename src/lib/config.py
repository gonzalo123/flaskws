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
