"""Command line debugger logging."""

import logging


def get_logger():
    """
    Sets up and returns logger with Singleton handler.

    :return: Command line logger
    :rtype: :class: `Logger`
    """
    logging.basicConfig(
        format='%(asctime)s %(processName)s %(levelname)s %(message)s',
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        logger.handlers.clear()
    return logger
