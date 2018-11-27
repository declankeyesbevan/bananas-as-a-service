#!/usr/bin/python

"""Runner entry point for command line execution of banana.py"""

# pylint: disable=invalid-name, broad-except, logging-fstring-interpolation

import json

from bananas_as_a_service.app import lambda_handler
from cli_tools.arg_parser import parse_args
from cli_tools.cli_logger import get_logger
from cli_tools.yaml_loader import load_yaml_file

logger = get_logger()

GENERAL_ERROR = 42
HTTP_OK = 200


def handler(event, context):
    """
    Command line runner for bananas_as_a_service.app.lambda_handler

    :param event: Details of HTTP request
    :type event: :class: `dict`
    :param context: Runtime information
    :type context: :class: `NoneType`
    """
    logger.info(f"Beginning execution for event: {event}")

    try:
        sentences = lambda_handler(event, context)
        if sentences.get('statusCode') != HTTP_OK:
            raise RuntimeError(f"RuntimeError in Lambda execution: {sentences.get('body')}")
    except Exception as exc:
        logger.exception(f"Exception in execution: {exc}")
        exit(GENERAL_ERROR)
    else:
        logger.info("Here are your bananas!")
        for sentence in json.loads(sentences.get('body')):
            logger.info(sentence)
        logger.info("Successful execution")


if __name__ == '__main__':
    # TODO: use real event and context
    args = parse_args()
    input_event = {
        'body': json.dumps(load_yaml_file(args.bananas))
    }
    input_context = None

    if args.performance:
        import cProfile
        cProfile.run('handler(input_event, input_context)')
    else:
        handler(input_event, input_context)
