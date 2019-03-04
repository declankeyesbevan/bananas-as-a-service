#!/usr/bin/env bash

cd webhooks
rm -rf build/*
virtualenv build/env
. build/env/bin/activate
pip install --upgrade pip
pip install -r webhook-requirements.txt -t build
cp branch_mutator.py build
mkdir build/cli_tools
cp ../cli_tools/cli_logger.py build/cli_tools/cli_logger.py
deactivate
rm -rf build/env
cd build
zip -vr webhook.zip *
aws lambda create-function \
    --function-name banana-branch-mutator \
    --zip-file fileb://webhook.zip \
    --handler branch_mutator.lambda_handler \
    --runtime python3.6 \
    --timeout 30 \
    --environment Variables="{AMAZON_ACCOUNT=${AMAZON_ACCOUNT},GITHUB_OWNER=${GITHUB_OWNER},GITHUB_SECRET=${GITHUB_SECRET},GITHUB_TOKEN=${GITHUB_TOKEN}}" \
    --role "arn:aws:iam::${AMAZON_ACCOUNT}:role/lambda-banana-role" \
    --profile ${AWS_PROFILE:=default}
