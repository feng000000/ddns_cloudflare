import threading
import requests
import logging
import time
from pathlib import Path
from datetime import datetime
from datetime import timedelta

from cloudflare import Cloudflare


API_TOKEN = "cfat_4vVI19jK1W7kVjBzigt1pIxVZUWYIdihSsoLD7nU76e108b3"
ZONE_ID = "1ea701e9fde418dc51a24ca505152bf2"
RECORD_NAME = "macmini.fengzer0.org"


def init_logging():
    log_file = Path("./ddns_updater.log")
    bkp_log_file = Path("./ddns_updater.log.bkp")

    if log_file.exists():
        log_file.replace(bkp_log_file)

    logging.basicConfig(
        filename=log_file,
        level="DEBUG",
        format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    )

    def init_logger(name: str, level: str):
        """specify logger's level"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

    init_logger("httpcore", "ERROR")
    init_logger("urllib3", "ERROR")
    init_logger("cloudflare", "INFO")
    init_logger("httpx", "ERROR")

    logging.info("init_logging done.")

client = Cloudflare(api_token=API_TOKEN)


def test_server():
    from flask import Flask
    from flask import request

    logger = logging.getLogger("TEST_SERVER")

    app = Flask(__name__)

    @app.route("/ping")
    def ping():
        logger.info(
            f"got ping from {request.remote_addr}, "
            f"Forwarded-For: {request.headers.get('X-Forwarded-For')}"
        )
        return "pong"

    app.run(host="::", port=5000, debug=False)



def update_dns():
    logger = logging.getLogger("DDNS")
    resp = client.dns.records.list(zone_id=ZONE_ID)

    for item in resp.result:
        if item.name != RECORD_NAME:
            continue

        logger.info(f"item.id: {item.id}")
        ip6_resp = requests.get(
            "http://6.ipw.cn",
            proxies={"http": None, "https": None},  # type: ignore
        )
        current_ipv6_addr = ip6_resp.text
        logger.info(f"current ipv6 address: {current_ipv6_addr}")

        update_resp = client.dns.records.edit(
            dns_record_id=item.id,
            zone_id=ZONE_ID,
            content=current_ipv6_addr,
            name=RECORD_NAME,
            ttl=300,
            type="AAAA",
        )
        if update_resp:
            logger.info(f"update result: {update_resp.to_json()}")
        else:
            logger.info("update failed, got None")


def update_loop():
    logger = logging.getLogger("DDNS")

    while True:
        try:
            current = datetime.now()
            logger.info(f">>>>>>>> run update_dns() on {current}")
            update_dns()
        except Exception as e:
            logger.error(f"update dns failed: {e!r}")

        next_run = datetime.now() + timedelta(seconds=300)
        logger.info(f" next run update_dns() on {next_run}\n\n")

        time.sleep(300)


if __name__ == "__main__":
    init_logging()

    server_t = threading.Thread(target=test_server)
    server_t.daemon = True
    server_t.start()

    update_loop()
