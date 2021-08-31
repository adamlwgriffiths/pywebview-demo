from textwrap import dedent
from cottonmouth.html import render
from cottonmouth.tags import *
from flask import Blueprint, request, session, url_for, current_app, render_template
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect

blueprint = Blueprint('base', __name__)
ws = Blueprint('ws', __name__)

@blueprint.route('/')
def home():
    return current_app.send_static_file('index.html')

@ws.route('join')
def join(message):
    print(f'join({message["room"]})')
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    # this isn't hooked up in brython, it's left here as an example of how to call sockets
    emit('my_response',
        {'data': 'In rooms: ' + ', '.join(rooms()), 'count': session['receive_count']})


@ws.route('leave')
def leave(message):
    print(f'leave({message["room"]})')
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    # this isn't hooked up in brython, it's left here as an example of how to call sockets
    emit('my_response',
        {'data': 'In rooms: ' + ', '.join(rooms()), 'count': session['receive_count']})


@ws.route('connect')
def connect():
    print(f'connect(): sid={request.sid}')
    # this isn't hooked up in brython, it's left here as an example of how to call sockets
    emit('my_response', {'data': 'Connected', 'count': 0})

@ws.route('disconnect_request')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect

    # this isn't hooked up in brython, it's left here as an example of how to call sockets
    emit('my_response',
        {'data': 'Disconnected!', 'count': session['receive_count']},
        callback=can_disconnect)
