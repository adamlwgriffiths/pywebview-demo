# monkey-patch pywebview's threading and url detection code
# https://github.com/r0x0r/pywebview/blob/master/webview/serving.py
import logging
logger = logging.getLogger(__name__)

def patch_socketio():
    import flask_socketio

    # this doesn't have to be monkey patched
    # but i suspect we'll get this rolled into a new version on gh
    # so lets just monkey patch for now
    class SocketIO(flask_socketio.SocketIO):
        '''Add support for socketio blueprints
        uses flask-sockets as a base'''
        def __init__(self, *args, **kwargs):
            self.blueprints = {}
            self._blueprint_order = []
            super(SocketIO, self).__init__(*args, **kwargs)

        def add_url_rule(self, rule, _, f, **options):
            self.on(rule, options.get('namespace'))(f)

        def register_blueprint(self, blueprint, **options):
            assert blueprint.name not in self.blueprints, f'A blueprint with the name {blueprint.name} is already registered'
            self.blueprints[blueprint.name] = blueprint
            self._blueprint_order.append(blueprint)

            blueprint.register(self, options)

    flask_socketio.SocketIO = SocketIO


def patch_pywebview():
    import threading
    import webview.serving

    def get_wsgi_server(app):
        if hasattr(app, '__webview_url'):
            # It's already been spun up and is running
            return app.__webview_url

        port = webview.serving._get_random_port()

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

    webview.serving.get_wsgi_server = get_wsgi_server
