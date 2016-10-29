import os
import sys
import time
import json

from flask import *
from werkzeug.contrib.fixers import ProxyFix
from glob import iglob
from queue import Queue, Empty
from threading import Thread
from redis import StrictRedis
from motionweb import utils
from motionweb import notifier

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config.update(
    DEBUG=os.environ.get('DEBUG', 'False') == 'True',
    SECRET_KEY=os.environ.get('SECRET_KEY', 'DEVELOPMENT'),
    MEDIA_FOLDER=os.environ.get('MEDIA_FOLDER', './media'),
    USERNAME=os.environ.get('USERNAME', 'admin'),
    PASSWORD=os.environ.get('PASSWORD', 'admin'),
)

clients = set()

@app.before_request
def check_auth():
    if request.path.startswith('/static') or request.endpoint == 'login':
        pass
    elif session.get('auth'):
        pass
    else:
        return redirect('/login')

@app.route("/")
def index():
    return redirect('/player')

@app.route("/player")
def player():
    return render_template('player.html')

@app.route("/subscribe")
def subscribe():
    queue = Queue()
    clients.add(queue)
    event_template = 'event: {type}\ndata: {data}\n\n'
    def gen():
        try:
            path_list = sorted(iglob(app.config['MEDIA_FOLDER'] + '/*.mp4'))
            video_list = []
            for path in path_list:
                filename = os.path.basename(path)
                video_list.append(utils.video_to_dict(filename))
            yield event_template.format(type='video:list', data=json.dumps(video_list))

            while True:
                try:
                    msg = queue.get(timeout=30)
                    filename = msg['data']
                    video = utils.video_to_dict(filename)
                    yield event_template.format(type='video:new', data=json.dumps(video))
                except Empty:
                    yield event_template.format(type='ping', data='')

        finally:
            clients.remove(queue)
    return Response(gen(), mimetype="text/event-stream")

@app.route("/media-lib/<video>")
def media_video(video):
    resp = make_response()
    resp.headers = { 'X-Accel-Redirect': '/media/' + video }
    return resp

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        session['auth'] = request.form['username'] == app.config['USERNAME'] \
                        and request.form['password'] == app.config['PASSWORD']
        return redirect('/')

@app.route("/logout")
def logout():
    session.pop('auth', None)
    return redirect('/')

@app.route("/clients")
def list_clients():
    return 'Connected Clients: {}'.format(len(clients))

#
# Services
#

def run_redis():
    redis = StrictRedis(decode_responses=True)
    subscription = redis.pubsub(ignore_subscribe_messages=True)
    subscription.subscribe('video:new')
    for msg in subscription.listen():
        [c.put(msg) for c in clients]

def start_redis():
    redis_thread = Thread(target=run_redis)
    redis_thread.setDaemon(True)
    redis_thread.start()

def main():
    start_redis()
    app.run(threaded=True)
