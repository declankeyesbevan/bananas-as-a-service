"""Lambda handler for processing input, output and exceptions."""

# pylint: disable=invalid-name, logging-fstring-interpolation, broad-except

import json

from bananas_as_a_service.app_logger import Logger
from bananas_as_a_service.banana import Banana

logger = Logger.get_logger()

HTTP_OK = 200
HTTP_INTERNAL_SERVER_ERROR = 500


def lambda_handler(event, context):
    """
    Top-level Banana Handler.

    :param event: Details of HTTP request
    :type event: :class: `dict`
    :param context: Runtime information
    :type context: :class: `LambdaContext`
    """
    logger.info(f"Beginning Lambda execution with context: {context}")

    body = json.loads(event.get('body'))
    logger.info(f"Lambda body: {body}")
    try:
        sentences = Banana().execute(body)
    except Exception as exc:
        # FIXME: handle exceptions more gracefully and return various HTTP error codes
        exc_message = "Exception in execution:"
        logger.exception(f"{exc_message} {exc}")
        return _create_body(HTTP_INTERNAL_SERVER_ERROR, f"{exc_message} {exc}")
    else:
        return _create_body(HTTP_OK, sentences)


def _create_body(status, body):
    return {
        'statusCode': status,
        'body': json.dumps(body),
    }
