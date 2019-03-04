#!/usr/bin/env bash

aws cloudformation create-stack \
    --stack-name ${INFRA_STACK} \
    --template-body file://infrastructure/cloudformation-infra.yml \
    --enable-termination-protection
