from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    LOG_FILE_PATH: Path = Path("./ddns_updater.log")
    BACKUP_LOG_FILE_PATH: Path = Path("./ddns_updater.log.bkp")
    API_TOKEN: str
    DOMAIN_NAME: str
    RECORD_NAME: str

    TEST_SERVER_PORT: int = 5001

config = Config()  # type: ignore
