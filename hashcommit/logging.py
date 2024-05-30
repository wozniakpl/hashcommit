import logging


def configure_logging(verbosity: int) -> None:
    log_level = logging.WARNING
    format_str = "[%(levelname)s] [%(asctime)s] %(message)s"
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG
        format_str = (
            "[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s"
        )

    logging.basicConfig(
        format=format_str,
        level=log_level,
    )
