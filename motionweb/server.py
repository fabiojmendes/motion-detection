import os
from flask import *
from glob import iglob

app = Flask(__name__)

app.config.update(
    DEBUG=os.environ.get('DEBUG', 'False') == 'True',
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24)),
    MEDIA_FOLDER=os.environ.get('MEDIA_FOLDER', './media'),
    USERNAME=os.environ.get('USERNAME', 'admin'),
    PASSWORD=os.environ.get('PASSWORD', 'admin'),
)

@app.before_request
def check_auth():
    if request.path.startswith('/static') or request.endpoint == 'login':
        pass
    elif not session.get('auth'):
        return redirect('/login')

@app.route("/")
def index():
    return redirect('/player')

@app.route("/player")
def player():
    return render_template('player.html')

@app.route("/playlist")
def playlist():
    videos = []
    path = app.config['MEDIA_FOLDER'] + '/*.mp4'
    for index, path in enumerate(iglob(path)):
        filename = os.path.basename(path)
        videos.append({
            'index': index,
            'filename': filename,
            'title': filename,
            'm4v': '/media-lib/' + filename
        })
    return jsonify(videos)

@app.route("/media-lib/<video>")
def media_video(video):
    resp = make_response()
    resp.headers = {
        'X-Accel-Redirect': '/media/' + video
    }
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

def main():
    app.run()
