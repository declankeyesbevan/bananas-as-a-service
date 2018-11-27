#!/usr/bin/env bash

aws ssm put-parameter \
    --name "app_id" \
    --value "${APP_ID}" \
    --type SecureString

aws ssm put-parameter \
    --name "app_key" \
    --value "${APP_KEY}" \
    --type SecureString
