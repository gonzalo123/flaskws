# Flask and websockets using Flask-SocketIO

Today we're going to create a simple Flask application with real time communication. We're going to use websocket 
with the SocketIO library. This library has an implementation for Python and Flask with [Flask-SocketIO]
(https://flask-socketio.readthedocs.io/). My idea is the following one. Websockets are bidirectional, but I only want 
to use the server to client communication within the websocket. For client to server I prefer to use the traditional 
HTTP communication. My application is going to have session based authentication. To simulate the login I have 
created a route called /login that creates a session. The idea is to use this authentication also for the websockets.
One important thing for me, in fact that's the main purpose of this post, is to allow sending websockets from outside 
the web application. Imagine for example that I want to send websockets to the client from a crontab or an external 
service. To do that we need to use a message queue to help SocketIO to communicate between web a client application. 
We're going to use a Redis server.

That's the main application

```python
from flask import Flask, render_template, session, request

from lib.ws import register_ws, emit_event, EmitWebsocketRequest
from settings import REDIS_HOST, WS_PATH

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

register_ws(app=app, socketio_path=WS_PATH, redis_host=REDIS_HOST)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    session['user'] = 'Gonzalo'
    return dict(name=session['user'])


@app.post('/api/')
def api():
    data = EmitWebsocketRequest(**request.json)
    emit_event(data.channel, data.body)

    return dict(status=True)

```

That's the html template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask-SocketIO Websocket Example</title>
    <script src="//cdn.socket.io/4.0.0/socket.io.min.js"></script>
</head>
<body>

<h1>Flask-SocketIO Websocket Example</h1>
<label for="message">Message:</label>
<input type="text" id="message" placeholder="type a message...">

<button onclick="sendMessage()">Send</button>
<ul id="messages"></ul>

<script>
    document.addEventListener("DOMContentLoaded", function () {
        let host = location.protocol + '//' + location.hostname + ':' + location.port
        let socket = io.connect(host, {
            path: '/ws/socket.io',
            reconnection: true,
            reconnectionDelayMax: 5000,
            reconnectionDelay: 1000
        });

        socket.on('connect', function () {
            console.log('Connected to ws');
        });

        socket.on('disconnect', function () {
            console.log('Disconnected from ws');
        });

        socket.on('message', function (msg) {
            let messages = document.getElementById('messages');
            let messageItem = document.createElement('li');
            messageItem.textContent = msg;
            messages.appendChild(messageItem);
        });

        window.sendMessage = async function () {
            const url = '/api/';
            const payload = {"channel": "message", "body": this.message.value};

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    console.error('Error: ' + response.statusText);
                }

                await response.json();
            } catch (error) {
                console.error('Error:', error);
            }
        };
    });
</script>
</body>
</html>
```
The register_ws function binds SocketIO to our Flask server. To allow sending messages outside our Flask application 
we need to create our socketio instance in two different ways. To do that I've created this ws.py file. Note: I'm using Pydantic for validate the http requests 

```python
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
```

And now we cand emit an event from outside the Flask application

```python
from lib.ws import emit_event, setup_ws
from settings import REDIS_HOST

setup_ws(redis_host=REDIS_HOST)
emit_event('message', 'Hi')
```
The application needs a redis server. I set up the server using docker

```yaml
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```