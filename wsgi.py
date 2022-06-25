import logging

from paste.translogger import TransLogger
from waitress import serve

from market.app import app

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    serve(TransLogger(app, setup_console_handler=False), host="0.0.0.0", port=80)
