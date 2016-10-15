import os
import flask
from flask import Flask

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    # USE_X_SENDFILE=True,
    # MEDIA_FOLDER='./media'
    MEDIA_FOLDER='/Users/fabiomendes/Desktop/motion-files'
))

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
    for i, f in enumerate(os.listdir(app.config['MEDIA_FOLDER'])):
        videos.append({
            'index': i,
            'filename': f,
            'title': f,
            'm4v': '/media/' + f
        })
    return flask.jsonify(videos)

@app.route("/media/<video>")
def media_video(video):
    print(video)
    # path = app.config['MEDIA_FOLDER'] + '/' + video
    resp = flask.make_response()
    resp.headers.set('X-Accel-Redirect', '/protected/media/' + video)
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
