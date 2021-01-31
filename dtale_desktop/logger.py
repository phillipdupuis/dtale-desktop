import logging

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s %(name)s %(asctime)s %(message)s"
)


def get_logger(name: str = "dtaledesktop") -> logging.Logger:
    return logging.getLogger(name)
