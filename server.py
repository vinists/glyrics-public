from os import environ
from threading import Thread, Event, active_count

from flask import Flask, render_template, url_for, session, request, redirect
from flask_socketio import SocketIO, join_room, close_room
from flask_cors import CORS
from flask_talisman import Talisman

from gevent import GreenletExit

from spotipy import SpotifyOAuth, is_token_expired
import spotipy.util as util
import spotipy

from util import composer, rndstring


app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = environ['SECRET_KEY']
app.config['CORS_HEADERS'] = 'Content-Type'


csp = {
    'default-src':[
        '\'self\'',
        '*.jquery.com',
        '*.cloudflare.com',
        '*.bootstrapcdn.com'
    ]
}
Talisman(app, content_security_policy=csp)

API_BASE = 'https://accounts.spotify.com'
REDIRECT_URI = "https://glyrics.herokuapp.com/auth"
SCOPE = 'user-read-currently-playing'

SHOW_DIALOG = True


# Spotify API keys

CLI_ID = environ['CLIENT_ID']
CLI_SEC = environ['CLIENT_SECRET']
CACHE = '.spotipyoauthcache'

socketio = SocketIO(app, async_mode=None, logger=True, cookie=None, engineio_logger=False, cors_allowed_origins=['https://glyrics.herokuapp.com', 'http://glyrics.herokuapp.com', 'https://code.jquery.com/jquery-3.5.0.min.js', 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.3.0/socket.io.slim.js', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css', API_BASE])

sp = SpotifyOAuth(client_id=CLI_ID,client_secret=CLI_SEC,
                        redirect_uri=REDIRECT_URI,cache_path=CACHE, scope=SCOPE)

thread = None

# Async Thread

def finder(token_full, room):
    
    while True:
        socketio.sleep(5)
        try:
            data = spotipy.Spotify(auth=token_full['access_token']).currently_playing()
            if data:
                song = data['item']['name']
                artist = data['item']['artists'][0]['name']
    
                if data['is_playing']:
                    socketio.emit('newsong', data=({'lyricsBody': 
                                            composer(artist, song).returner()}),
                                            namespace='/data', room=room)
        except (spotipy.client.SpotifyException, GreenletExit, TypeError) as e:
            print("Exception: ", e)
            if(is_token_expired(token_full)):
                print("Token refreshing auto")
                token_full = sp.refresh_access_token(token_full['refresh_token'])
            if(type(e) is GreenletExit):
                break


def lyrics_connect():
    join_room(session.get('room'))
    global thread
    print('Client connected')
    try:
        print('Starting Thread!')
        thread = socketio.start_background_task(finder, session.get('token_info'), session.get('room'))
    except Exception:
        print('lyrics_connect exception:', Exception)
        pass

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html") 

@app.route('/lyrics', methods=['GET'])
def lyrics():

    if session.get('room') == None:
        session.clear()
        session['room'] = rndstring()

    if session.get('token_info') is None:
        auth_url = sp.get_authorize_url()
        print('Getting "authorize_url" for new token.')
        return redirect(auth_url)
    else:
        if(is_token_expired(session.get('token_info'))):
            print("Token refreshed with route.")
            session['token_info'] = sp.refresh_access_token(session.get('token_info').get('refresh_token'))

        socketio.on_event('connect', lyrics_connect, namespace='/data')        
        return render_template('lyrics.html')




@app.route('/auth')
def auth():
    session['token_info'] = sp.get_access_token(request.args.get('code'), check_cache=False)
    return redirect(url_for("lyrics"))



@socketio.on('disconnect', namespace='/data')
def disconnect():
    close_room(session.get('room'))
    if(thread):
        thread.kill()
    session.pop('room', None)
    print('Client Disconnected. Threads on:', active_count())
    



if __name__ == "__main__":
    socketio.run(app)