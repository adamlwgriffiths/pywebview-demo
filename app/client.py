import monkey_patch
monkey_patch.patch_pywebview()

from contextlib import redirect_stdout
from io import StringIO
import logging
import sys
from threading import Thread
import webview
import app

logger = logging.getLogger(__name__)

def run():
    gui = {
        'win32': 'cef', # msHTML doesn't support websockets: https://github.com/r0x0r/pywebview/issues/534
        'linux': 'gtk',
    }[sys.platform]

    window = webview.create_window('MUD', app.create_app())
    webview.start(gui=gui, debug=__debug__)


if __name__ == '__main__':
    run()
