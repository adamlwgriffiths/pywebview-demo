from browser import window, document, alert
io = window.io

# brython has its own markdown renderer
# but it doesnt currently render images correctly
# https://github.com/brython-dev/brython/issues/1761
# once its fixed, use brython's one instead
marked = window.marked
DOMPurify = window.DOMPurify


markdown = DOMPurify.sanitize(marked('''
# Marked in the browser

Rendered by **marked**.
'''))
document['content'].innerHTML = markdown



socket = io()
def on_connect():
    document['status'].innerHTML = ('connected in brython')
    socket.emit('join', {'room': 'asd'})

socket.on('connect', on_connect)
