import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    # logging.basicConfig(
    #     level=logging.WARNING,
    #     format="|%(asctime)s||%(name)s||%(levelname)s|\n%(message)s",
    #     datefmt="%Y-%m-%d %H:%M:%S",
    # )

    # InterceptHandler를 루트 로거에 추가하여 모든 로그 메시지를 loguru로 전달
    for name in logging.root.manager.loggerDict:
        if name in ("uvicorn"):
            uvicorn_logger = logging.getLogger(name)
            uvicorn_logger.handlers.clear()
            uvicorn_logger.setLevel(logging.INFO)
            uvicorn_logger.addHandler(InterceptHandler())
