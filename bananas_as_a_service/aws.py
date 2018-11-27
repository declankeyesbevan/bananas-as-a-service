"""Utilities for interacting with AWS via boto3"""

# pylint: disable=invalid-name, logging-fstring-interpolation

import os

import boto3

from botocore.exceptions import ProfileNotFound, SSLError, ClientError, ConnectTimeoutError

from bananas_as_a_service.app_logger import Logger
from bananas_as_a_service.error_handler import GeneralError

logger = Logger().get_logger()


def connect_to_aws_resource(resource_name):
    """
    Pass in the AWS service and return a boto3 resource.

    :param resource_name: Name of AWS service
    :type resource_name: :class: `str`
    :return: boto3 resource
    :rtype: :class: `boto3.resource`
    """
    logger.info(f"Attempting connection to AWS resource: {resource_name}")

    try:
        resource = boto3.resource(
            resource_name, region_name=os.environ.get('AWS_REGION'), verify=True)
    except ConnectTimeoutError as err:
        raise GeneralError(f"Timeout connecting to AWS: {err}")
    except ProfileNotFound as err:
        raise GeneralError(f"Could not find AWS profile: {err}")
    except SSLError as err:
        raise GeneralError(f"SSL Error: {err}")
    else:
        return resource


def connect_to_aws_client(client_name):
    """
    Pass in the AWS service and return a boto3 client.

    :param client_name: Name of AWS service
    :type client_name: :class: `str`
    :return: boto3 resource
    :rtype: :class: `boto3.client`
    """
    logger.info(f"Attempting connection to AWS client: {client_name}")

    try:
        client = boto3.client(
            client_name, region_name=os.environ.get('AWS_REGION'), verify=True)
    except ConnectTimeoutError as err:
        raise GeneralError(f"Timeout connecting to AWS: {err}")
    except ProfileNotFound as err:
        raise GeneralError(f"Could not find AWS profile: {err}")
    except SSLError as err:
        raise GeneralError(f"SSL Error: {err}")
    else:
        return client


def get_from_parameter_store(parameters):
    """
    Pass in a list of parameters to access in Systems Manager Parameter Store.

    :param parameters: Key names to look up
    :type parameters: :class: `list`
    :return: Values of keys
    :rtype: :class: `dict`
    """
    logger.info(f"Attempting lookup of parameters: {parameters}")

    ssm_parameters = {}
    try:
        for param in parameters:
            this_param = connect_to_aws_client('ssm').get_parameter(Name=param, WithDecryption=True)
            ssm_parameters.update({
                this_param.get('Parameter').get('Name'): this_param.get('Parameter').get('Value')})
    except ProfileNotFound as err:
        raise GeneralError(f"Could not find AWS profile: {err}")
    except ClientError as err:
        raise GeneralError(f"Error getting parameters from Parameter Store: {err}")
    else:
        return ssm_parameters
