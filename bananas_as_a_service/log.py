"""
Defines application logging.
"""

# pylint: disable=too-few-public-methods

import logging


class Logger:
    """
    Initialise application logger.
    """

    @classmethod
    def get_logger(cls):
        """
        Sets up and returns logger with Singleton handler.
        :return: Application logger
        :rtype: :class: `Logger`
        """

        logging.basicConfig(
            format='%(asctime)s %(processName)s %(levelname)s %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)
        if logger.hasHandlers():
            logger.handlers.clear()
        return logger
