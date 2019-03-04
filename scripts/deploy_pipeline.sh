#!/usr/bin/env bash

aws cloudformation create-stack \
    --stack-name ${PIPELINE_STACK} \
    --template-body file://infrastructure/cloudformation-pipeline.yml \
    --enable-termination-protection
