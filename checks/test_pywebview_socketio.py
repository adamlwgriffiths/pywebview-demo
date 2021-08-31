####################################################
# Monkey patching

# https://gist.github.com/punchagan/53600958c1799c2dcf26
import webview
import webview.serving
import threading
from webview.serving import ThreadingWSGIServer, WSGIRequestHandler11
import socketio


def get_wsgi_server(app):
    print('CUSTOM get_wsgi_server')
    if hasattr(app, '__webview_url'):
        # It's already been spun up and is running
        return app.__webview_url

    port = webview.serving._get_random_port()

    #server = wsgiref.simple_server.make_server(
    #    'localhost', port, app, server_class=ThreadingWSGIServer,
    #    handler_class=WSGIRequestHandler11,
    #)

    # deploy with eventlet
    def run_server():
        import eventlet
        import eventlet.wsgi
        eventlet.wsgi.server(eventlet.listen(('', port)), app)

    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    app.__webview_url = 'http://localhost:{0}/'.format(port)
    logger.debug('HTTP server for {!r} started on {}'.format(app, app.__webview_url))

    return app.__webview_url


# https://gist.github.com/punchagan/53600958c1799c2dcf26
import webview.serving
def resolve_url(url, should_serve):
    print('CUSTOM RESOLVE URL')
    return get_wsgi_server(url)

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

@html_blueprint.route('/')
def home():
    print('Serving /')
    return '''
        <html>
        <head>
            <title>pywebview</title>
            <meta charset="utf-8">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.3/socket.io.min.js"></script>
            <script type="text/javascript">
                (function() {
                    document.write("initialising socket");
                    const socket = io();

                    socket.on('connect', () => {
                        alert(`connect ${socket.id}`);
                    });

                    socket.on('disconnect', () => {
                        alert(`disconnect ${socket.id}`);
                    });

                    socket.on('hello', (a, b, c) => {
                        document.write(a, b, c);
                    });
                })();
            </script>
        </head>
        <body>
            THIS IS A TEMPLATE
        </body>
        </html>
    '''


###############################
# app.py
from functools import wraps
from flask import Flask, request
import webview

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

    app.sio = socketio.Server(logger=True, async_mode=None)
    app.wsgi_app = socketio.WSGIApp(app.sio, app.wsgi_app)

    @app.sio.event
    def connect(sid, environ, auth):
        print(f'connected auth={auth} sid={sid}')
        app.sio.emit('hello', (1, 2, {'hello': 'you'}), to=sid)

    @app.sio.event
    def disconnect(sid):
        print('disconnected', sid)

    app.after_request(add_header)
    app.register_blueprint(html_blueprint)
    return app


###############################
# client.py

def run():
    window = webview.create_window('MUD', create_app())
    webview.start(gui='cef', debug=__debug__)

if __name__ == '__main__':
    run()
