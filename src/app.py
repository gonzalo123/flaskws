from flask import Flask, render_template, session, request

from lib.ws import register_ws, emit_event, EmitWebsocketRequest
from settings import REDIS_HOST, WS_PATH

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

register_ws(app=app, redis_host=REDIS_HOST, socketio_path=WS_PATH)


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
