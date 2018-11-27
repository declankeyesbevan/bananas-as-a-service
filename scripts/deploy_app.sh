#!/usr/bin/env bash

sam package \
    --template-file infrastructure/cloudformation-app.yml \
    --output-template-file packaged-app.yml \
    --s3-bucket ${BUCKET_NAME}

sam deploy \
    --template-file packaged-app.yml \
    --stack-name ${APP_STACK} \
    --capabilities CAPABILITY_IAM

aws cloudformation describe-stacks \
    --stack-name ${APP_STACK} \
    --query 'Stacks[].Outputs'
