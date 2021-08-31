# Pywebview + SocketIO + Brython

## Usage

Run:

    python app/client.py
    # or
    ./bin/client

## Update brython minified libraries:

    ./bin/build_brython_modules

Comment out the `brython_stdlib.js` script tag.

Uncomment the `brython_modules.js` script tag.

Enjoy faster loading of your Python code.
