import logging


def setup_logging():
    logging.basicConfig(
        level=logging.WARNING,
        format="|%(asctime)s||%(name)s||%(levelname)s|\n%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
