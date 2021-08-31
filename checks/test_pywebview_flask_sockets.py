# https://gist.github.com/punchagan/53600958c1799c2dcf26
import webview.serving
def resolve_url(url, should_serve):
    print('CUSTOM RESOLVE URL')
    return 'http://127.0.0.1:5000'
webview.serving.resolve_url = resolve_url
webview.window.resolve_url = resolve_url

from contextlib import contextmanager, redirect_stdout
from io import StringIO
import logging
import sys
from threading import Thread
import webview

logger = logging.getLogger(__name__)


###############################
# views.py
from textwrap import dedent
from cottonmouth.html import render
from cottonmouth.tags import *
from flask import Blueprint, request, url_for, current_app, render_template

html_blueprint = Blueprint('base', __name__)
ws_blueprint = Blueprint('ws', __name__)

@html_blueprint.route('/')
def home():
    return '''
        <html>
        <head>
            <title>pywebview</title>
            <meta charset="utf-8">
            <script type="text/javascript">
                var loc = window.location;
                var new_uri = (loc.protocol === "https:") ? "wss:" : "ws:";
                new_uri += "//" + loc.host + "/echo";

                alert(new_uri);

                var ws = new WebSocket(new_uri);
                ws.onopen = function() {
                    ws.send("socket open");
                };
                ws.onclose = function(evt) {
                    alert("socket closed");
                };
                ws.onmessage = function(evt) {
                    alert(evt.data);
                };
            </script>
        </head>
        <body>
            THIS IS A TEMPLATE
        </body>
        </html>

    '''

@ws_blueprint.route('/echo')
def echo_socket(socket):
    while not socket.closed:
        message = socket.receive()
        print('Received', message)
        socket.send(message)


###############################
# app.py
from functools import wraps
from flask import Flask, request
#from flask_socketio import SocketIO
from flask_sockets import Sockets
import webview

#import eventlet
#eventlet.monkey_patch()


def verify_token(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        data = json.loads(request.data)
        token = data.get('token')
        if token == webview.token:
            return function(*args, **kwargs)
        else:
            raise Exception('Authentication error')
    return wrapper

def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching
    #socketio = SocketIO(app)
    sockets = Sockets(app)

    app.after_request(add_header)
    app.register_blueprint(html_blueprint)
    sockets.register_blueprint(ws_blueprint)
    return app


###############################
# client.py
@contextmanager
def create_server():
    host, port = '127.0.0.1', 5000
    def run_server(host, port):
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        server = pywsgi.WSGIServer(('', 5000), create_app(), handler_class=WebSocketHandler)
        server.serve_forever()

    thread = Thread(target=run_server, args=(host, port))
    thread.daemon = True
    thread.start()
    yield (host, port)

def run():
    gui = {
        'win32': 'cef', # msHTML doesn't support websockets
        'linux': 'gtk',
    }[sys.platform]

    with create_server() as (host, port):
        window = webview.create_window('MUD', f'https://{host}:{port}')
        webview.start(gui=gui, debug=__debug__)

if __name__ == '__main__':
    run()
