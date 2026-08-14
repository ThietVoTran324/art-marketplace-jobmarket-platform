import logging.config

import yaml

from app.config import settings

with open("logging-config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

config["handlers"]["server_error_file"]["filename"] = settings.LOGS_PATH + "server_errors.jsonl"
config["handlers"]["requests_file"]["filename"] = settings.LOGS_PATH + "requests.jsonl"
config["handlers"]["client_errors_file"]["filename"] = (
    settings.LOGS_PATH + "client_errors.jsonl"
)

logging.config.dictConfig(config)

logger = logging.getLogger("pinterest_api_logger")
requests_logger = logging.getLogger("requests_logger")
client_errors_logger = logging.getLogger("client_errors_logger")
