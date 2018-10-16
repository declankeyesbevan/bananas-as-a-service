#!/usr/bin/python

"""
Runner entry point for command line execution of banana.py
"""

# pylint: disable=invalid-name, broad-except, logging-fstring-interpolation

from bananas_as_a_service.banana import Banana
from bananas_as_a_service.log import Logger

GENERAL_ERROR = 42
logger = Logger.get_logger()


def handler():
    """
    Top-level exception handling runner for banana.py.
    """
    logger.info("Beginning execution")

    try:
        Banana().execute()
    except Exception as exc:
        logger.exception(f"Exception in execution: {exc}")
        exit(GENERAL_ERROR)
    else:
        logger.info("Successful execution")


if __name__ == '__main__':
    handler()