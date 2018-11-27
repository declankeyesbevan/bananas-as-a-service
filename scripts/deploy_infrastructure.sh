#!/usr/bin/env bash

aws cloudformation create-stack \
    --stack-name ${INFRA_STACK} \
    --template-body file://infrastructure/cloudformation-infra.yml \
    --enable-termination-protection

aws cloudformation describe-stacks \
    --stack-name ${INFRA_STACK} \
    --query 'Stacks[].Outputs'
