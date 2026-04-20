import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        format='{"level":"%(levelname)s","message":"%(message)s"}',
        stream=sys.stdout,
        level=level.upper(),
    )
