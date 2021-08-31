import monkey_patch
monkey_patch.patch_socketio()

from functools import wraps
from flask import Flask, Blueprint, request
import flask_socketio
import views


def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.socketio = flask_socketio.SocketIO(app, async_mode='eventlet')

    # disable caching
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
    app.after_request(add_header)

    views.register_blueprints(app)
    return app

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi

    app = create_app()
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
