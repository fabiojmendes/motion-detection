import os
import json

from flask import *
from werkzeug.contrib.fixers import ProxyFix
from glob import iglob
from queue import Queue
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

@app.route("/playlist")
def playlist():
    path_list = sorted(iglob(app.config['MEDIA_FOLDER'] + '/*.mp4'))
    start = request.args.get('start')
    videos = []
    for path in path_list:
        filename = os.path.basename(path)
        if start and filename <= start:
            continue
        videos.append(utils.video_to_dict(filename))
    return jsonify(videos)

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

@app.route("/subscribe")
def subscribe():
    queue = Queue()
    clients.add(queue)
    def gen():
        try:
            while True:
                msg = queue.get()
                filename = msg['data']
                video = utils.video_to_dict(filename)
                yield 'id: {}\ndata: {}\n\n'.format(filename, json.dumps(video))
        finally:
            clients.remove(queue)
    return Response(gen(), mimetype="text/event-stream")

def run_redis():
    redis = StrictRedis(decode_responses=True)
    subscription = redis.pubsub(ignore_subscribe_messages=True)
    subscription.subscribe('video:new')
    for msg in subscription.listen():
        for c in clients:
            c.put(msg)

def main():
    # notifier.start()
    redis_thread = Thread(target=run_redis)
    redis_thread.setDaemon(True)
    redis_thread.start()

    app.run(threaded=True)
