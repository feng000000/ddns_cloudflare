import logging
import threading
from flask import Flask
from flask import request

from config import config

def run_test_server():
    server_t = threading.Thread(target=_test_server)
    server_t.daemon = True
    server_t.start()

def _test_server():

    logger = logging.getLogger("TEST_SERVER")
    logger.setLevel("DEBUG")

    app = Flask(__name__)

    @app.route("/ping")
    def ping():
        logger.info(
            f"got ping from {request.remote_addr}, "
            f"Forwarded-For: {request.headers.get('X-Forwarded-For')}"
        )
        return "pong"

    app.run(host="::", port=config.TEST_SERVER_PORT, debug=False)
