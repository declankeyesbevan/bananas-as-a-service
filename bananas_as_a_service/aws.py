import os

import boto3

from botocore.exceptions import ProfileNotFound, SSLError

from bananas_as_a_service.log import Logger
from error_handler import GeneralError

logger = Logger().get_logger()


def connect_to_aws_resource(resource_name):
    try:
        resource = boto3.resource(
            resource_name, region_name=os.environ.get('AWS_REGION'), verify=True)
    except ProfileNotFound as err:
        raise GeneralError(f"Could not find AWS profile: {err}")
    except SSLError as err:
        raise GeneralError(f"SSL Error: {err}")
    else:
        return resource
