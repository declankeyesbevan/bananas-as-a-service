#!/usr/bin/env bash

sam local start-api --template infrastructure/cloudformation-app.yml \
    --debug-port ${DEBUG_PORT} \
    --profile ${AWS_PROFILE:=default} \
    --debug
