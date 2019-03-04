#!/usr/bin/env bash

aws cloudformation create-stack \
    --stack-name ${IAM_STACK} \
    --template-body file://infrastructure/cloudformation-iam.yml \
    --enable-termination-protection
