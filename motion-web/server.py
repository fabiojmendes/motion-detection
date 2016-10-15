import os
import flask

from flask import Flask
from glob import iglob

app = Flask(__name__)

app.config.update(
    DEBUG=os.environ.get('DEBUG', False),
    SECRET_KEY=os.environ.get('SECRET_KEY', 'development key'),
    MEDIA_FOLDER=os.environ.get('MEDIA_FOLDER', './media')
)

@app.route("/")
def index():
    if flask.session.get('auth'):
        return flask.redirect('/player')
    else:
        return flask.redirect('/login')

@app.route("/player")
def player():
    return flask.render_template('player.html')

@app.route("/playlist")
def playlist():
    videos = []
    for index, path in enumerate(iglob(app.config['MEDIA_FOLDER'] + '/*.mp4')):
        filename = os.path.basename(path)
        videos.append({
            'index': index,
            'filename': filename,
            'title': filename,
            'm4v': '/media-lib/' + filename
        })
    return flask.jsonify(videos)

@app.route("/media-lib/<video>")
def media_video(video):
    resp = flask.make_response()
    resp.headers = {
        'X-Accel-Redirect': '/media/' + video
    }
    return resp


@app.route("/login", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    elif flask.request.method == 'POST':
        flask.session['auth'] = True
        return flask.redirect('/')

@app.route("/logout")
def logout():
    flask.session.pop('auth', None)
    return flask.redirect('/')
# if __name__ == "__main__":
#     app.run()
