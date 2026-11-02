"""AppLogger: the single logging entry point. Logs go to stderr; stdout carries the report."""

import logging
import sys


class AppLogger:
    _configured = False

    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)

    @classmethod
    def configure(cls, level: str) -> None:
        if cls._configured:
            return
        logging.basicConfig(
            level=level.upper(), stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s"
        )
        cls._configured = True

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)
