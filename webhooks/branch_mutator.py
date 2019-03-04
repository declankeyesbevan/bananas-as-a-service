"""
Receives a Webhook from GitHub when a branch is created or deleted. Parses the payload, downloads
the source from GitHub, transforms the CloudFormation template and then executes it. The idea is to
dynamically create a CI/CD CodePipeline execution for every feature branch created in GitHub. And
then destroy it when the branch is deleted.

It was attempted to do all of this in CodePipeline. Essentially a CodePipeline which creates
CodePipelines. However every new feature branch pipeline was considered a replacement for the
existing one managed by CloudFormation in the deploy stage.
"""
import json
import os

from urllib import request
from urllib.error import URLError
from zipfile import ZipFile, BadZipFile

from boto3 import client
from botocore.exceptions import ClientError
from cfn_flip import to_json

from cli_tools.cli_logger import get_logger

logger = get_logger()

HTTP_OK = 200
HTTP_CLIENT_ERR = 400
HTTP_SERVER_ERR = 500
REGION_NAME = 'ap-southeast-2'


def lambda_handler(event, context):
    logger.info(f"Starting Lambda execution with context: {context}")

    # Instead of creating custom exceptions, use RuntimeError for Client and SystemError for Server.
    response_body = None
    try:
        branch, event_type = _parse_headers(event)
        secrets = _get_secrets()

        if event_type == 'create':
            _scrub()
            _source(branch, secrets)
            template, params = _build(branch, secrets)
            response_body = _deploy(branch, template, params, secrets)
        elif event_type == 'delete':
            response_body = _delete(branch, secrets)
    except RuntimeError as err:
        logger.error(f"RuntimeError: {err}")
        return _create_response(HTTP_CLIENT_ERR, err)
    except SystemError as err:
        logger.error(f"SystemError: {err}")
        return _create_response(HTTP_SERVER_ERR, err)
    else:
        return _create_response(HTTP_OK, response_body)


def _create_response(response_code, response_body):
    # Can't JSON serialise an exception by default so let's be lazy and just stringify it.
    return {
        'statusCode': response_code,
        'body': json.dumps(response_body) if response_code == HTTP_OK else str(response_body)
    }


def _parse_headers(event):
    try:
        headers = event['headers']
        event_type = headers['X-GitHub-Event']
        body = json.loads(event['body'])
        branch = body['ref']
    except KeyError as err:
        raise RuntimeError(f"{err} with event: {event} ")
    else:
        logger.info(f"Headers: {headers}")
        logger.info(f"Event Type: {event_type}")
        logger.info(f"Body: {body}")
        logger.info(f"Branch Name: {branch}")

        return branch, event_type


def _scrub():
    logger.info("Scrubbing")

    # Lambda containers can be re-used so we need to scrub the /tmp dir
    for root, _, files in os.walk('/tmp'):
        for file in files:
            os.remove(os.path.join(root, file))


def _get_secrets():
    logger.info("Getting secrets")

    params = ['github_secret', 'github_token', 'github_owner', 'amazon_account']
    ssm_parameters = {}
    try:
        for param in params:
            this_param = client(
                'ssm', region_name=REGION_NAME).get_parameter(Name=param, WithDecryption=True)
            ssm_parameters.update({
                this_param.get('Parameter').get('Name'): this_param.get('Parameter').get('Value')})
    except ClientError as err:
        raise SystemError(f"{err} getting parameters from Parameter Store")
    else:
        return ssm_parameters


def _source(branch, secrets):
    logger.info("Sourcing")

    url = (
        f"https://github.com/{secrets.get('github_owner')}/"
        f"bananas-as-a-service/archive/{branch}.zip"
    )
    logger.info("Download from GitHub started")
    try:
        filename, _ = request.urlretrieve(url, filename="/tmp/banana.zip")
    except URLError as err:
        raise RuntimeError(f"{err} in URL: {url}")
    else:
        logger.info("Download from GitHub complete")

    try:
        with ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall('/tmp')
    except BadZipFile as err:
        raise SystemError(f"{err} opening zip file: {filename}")
    else:
        logger.info(f"Zip file: {filename} opened")


def _build(branch, secrets):
    logger.info("Building")

    template = _load_template(branch)
    params = _create_parameters(branch, secrets)
    return template, params


def _load_template(branch):
    logger.info("Loading template")

    directory = f'/tmp/bananas-as-a-service-{branch}/infrastructure'
    template = f'{directory}/cloudformation-pipeline.yml'
    try:
        with open(template) as yaml_file:
            data = json.loads(to_json(yaml_file))
            if not data:
                raise RuntimeError(f"YAML file: {template} is empty")
    except (IOError, FileNotFoundError) as err:
        raise SystemError(f"{err}")
    else:
        return data


def _create_parameters(branch, secrets):
    logger.info("Creating parameters")

    github_secret = secrets.get('github_secret')
    github_token = secrets.get('github_token')
    github_owner = secrets.get('github_owner')
    amazon_account = secrets.get('amazon_account')  # Can't start param with `aws`

    # Why on earth AWS forces us to use this horrible data structure when using CloudFormation
    # with boto3 is beyond me... why can't I just pass the json file like a normal person?
    keys = [
        'ApplicationStackName',
        'ArtifactStoreBucket',
        'BuildName',
        'BuildRole',
        'ChangeSetName',
        'CloudFormationRole',
        'GitHubBranch',
        'GitHubRepo',
        'GitHubOwner',
        'GitHubSecret',
        'GitHubToken',
        'PipelineRole',
        'PipelineName',
        'PipelineWebhookName',
    ]
    values = [
        f'banana-{branch}-app',
        'bananas-as-a-service',
        f'banana-{branch}-build',
        f'arn:aws:iam::{amazon_account}:role/codebuild-banana-role',
        f'banana-{branch}-changeset',
        f'arn:aws:iam::{amazon_account}:role/cloudformation-banana-role',
        f'{branch}',
        'bananas-as-a-service',
        f'{github_owner}',
        f'{github_secret}',
        f'{github_token}',
        f'arn:aws:iam::{amazon_account}:role/codepipeline-banana-role',
        f'banana-{branch}-pipeline',
        f'banana-{branch}-webhook',
    ]
    return [{'ParameterKey': keys[i], 'ParameterValue': values[i]} for i, _ in enumerate(keys)]


def _deploy(branch, template, params, secrets):
    logger.info("Deploying")

    cloudformation_client = client('cloudformation', region_name=REGION_NAME)
    amazon_account = secrets.get('amazon_account')

    try:
        response = cloudformation_client.create_stack(
            StackName=f'banana-{branch}-pipeline',
            TemplateBody=json.dumps(template),
            Parameters=params,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            RoleARN=f'arn:aws:iam::{amazon_account}1:role/cloudformation-banana-role',
        )
    except ClientError as err:
        raise SystemError(f"{err} deploying with CloudFormation")
    else:
        return response


def _delete(branch, secrets):
    logger.info("Deleting")

    cloudformation_client = client('cloudformation', region_name=REGION_NAME)
    amazon_account = secrets.get('amazon_account')

    resources_to_delete = [f'banana-{branch}-app', f'banana-{branch}-pipeline']
    responses = []
    try:
        for resource in resources_to_delete:
            responses.append(
                cloudformation_client.delete_stack(
                    StackName=resource,
                    RoleARN=f'arn:aws:iam::{amazon_account}:role/cloudformation-banana-role',
                )
            )
    except ClientError as err:
        raise SystemError(f"{err} deleting with CloudFormation")
    else:
        return responses
