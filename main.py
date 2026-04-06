import threading
import requests
import logging
import time
from datetime import datetime
from datetime import timedelta

from cloudflare import Cloudflare
from config import config
from test_server import run_test_server
from disable_temp_ipv6 import disable_ipv6_temp_addresses

def init_logging():
    if config.LOG_FILE_PATH.exists():
        config.LOG_FILE_PATH.replace(config.BACKUP_LOG_FILE_PATH)

    logging.basicConfig(
        filename=config.LOG_FILE_PATH,
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



def update_dns(client: Cloudflare):
    logger = logging.getLogger("DDNS")

    # get zone id
    zone_id = None
    for item in client.zones.list().result:
        if item.name == config.DOMAIN_NAME:
            zone_id = item.id
            break
    assert zone_id is not None, f"None zone id for {config.DOMAIN_NAME}"

    # find record
    for item in client.dns.records.list(zone_id=zone_id).result:
        if item.name != config.RECORD_NAME:
            continue

        logger.info(f"item.id: {item.id}")
        ip6_resp = requests.get(
            "http://6.ipw.cn",
            proxies={"http": None, "https": None},  # type: ignore
        )
        current_ipv6_addr = ip6_resp.text

        if current_ipv6_addr == item.content:
            logger.info(
                f"record content not changed, skip update: {item.content}"
            )
            return

        logger.info(f"current ipv6 address: {current_ipv6_addr}")

        # update record
        update_resp = client.dns.records.edit(
            dns_record_id=item.id,
            zone_id=zone_id,
            content=current_ipv6_addr,
            name=config.RECORD_NAME,
            ttl=300,
            type="AAAA",
        )
        if update_resp:
            logger.info(f"update result: {update_resp.to_json()}")
        else:
            logger.info("update failed, got response None")


def update_loop():
    logger = logging.getLogger("DDNS")

    client = Cloudflare(api_token=config.API_TOKEN)
    while True:
        try:
            current = datetime.now()
            logger.info(f">>>>>>>> run update_dns() on {current}")
            update_dns(client)
        except Exception as e:
            logger.error(f"update dns failed: {e!r}")

        logger.error(
            f"update dns success: {config.RECORD_NAME}\n"
            f"request http://{config.RECORD_NAME}:{config.TEST_SERVER_PORT}/ping to check"
        )

        next_run = datetime.now() + timedelta(seconds=300)
        logger.info(f">>>>>>>> next run update_dns() on {next_run}\n\n")

        time.sleep(300)


if __name__ == "__main__":
    init_logging()
    disable_ipv6_temp_addresses()

    run_test_server()

    update_loop()
