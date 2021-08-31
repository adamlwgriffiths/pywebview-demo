from . import basic

def register_blueprints(app):
    app.register_blueprint(basic.blueprint)
    app.socketio.register_blueprint(basic.ws)
