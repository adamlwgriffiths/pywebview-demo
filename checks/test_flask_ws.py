# Copy of http://stackoverflow.com/a/20104705
from flask import Flask
from flask_sockets import Sockets

app = Flask(__name__)
app.debug = True

sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message[::-1])

@app.route('/')
def hello():
    return '''
        <html>
        <head>
            <title>pywebview</title>
            <meta charset="utf-8">

            <script type="text/javascript">
                var ws = new WebSocket("ws://127.0.0.1:33102/echo");
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
        </body>
        </html>
    '''

@app.route('/echo_test', methods=['GET'])
def echo_test():
    return "HELLO"

if __name__ == '__main__':
    #app.run()
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
