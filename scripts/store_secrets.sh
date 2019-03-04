#!/usr/bin/env bash

aws ssm put-parameter \
    --name "app_id" \
    --value "${APP_ID}" \
    --type SecureString

aws ssm put-parameter \
    --name "app_key" \
    --value "${APP_KEY}" \
    --type SecureString

aws ssm put-parameter \
    --name "amazon_account" \
    --value "${AMAZON_ACCOUNT}" \
    --type SecureString

aws ssm put-parameter \
    --name "github_owner" \
    --value "${GITHUB_OWNER}" \
    --type SecureString

aws ssm put-parameter \
    --name "github_secret" \
    --value "${GITHUB_SECRET}" \
    --type SecureString

aws ssm put-parameter \
    --name "github_token" \
    --value "${GITHUB_TOKEN}" \
    --type SecureString
