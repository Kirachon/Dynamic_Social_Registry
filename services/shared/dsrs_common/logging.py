import json
import logging
import os
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": getattr(record, "asctime", None) or self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)

def configure_logging(level: str = "INFO"):
    handler = logging.StreamHandler(sys.stdout)
    if os.getenv("LOG_JSON") == "1":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
    logging.getLogger("uvicorn.access").handlers = []

