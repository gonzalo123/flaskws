from flask import Flask, render_template, session
from flask_pydantic import validate

from lib.ws import register_ws, emit_event
from lib.models import EmitWebsocketRequest
from settings import REDIS_HOST, WS_PATH, SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

register_ws(app=app, redis_host=REDIS_HOST, socketio_path=WS_PATH)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    session['user'] = 'Gonzalo'
    return dict(name=session['user'])


@app.post('/api/')
@validate()
def api(body: EmitWebsocketRequest):
    emit_event(body.channel, body.body)

    return dict(status=True)
