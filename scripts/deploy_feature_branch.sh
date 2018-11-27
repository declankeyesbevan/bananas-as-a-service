#!/usr/bin/env bash

git_branch=`git branch -a --contains HEAD | sed -n 2p | awk '{ printf $1 }'`
master_branch=master

if test "${git_branch#*$master_branch}" = "$git_branch"
    then
        sam deploy \
            --template-file packaged-app.yml \
            --stack-name bananas-as-a-service-${git_branch}-app \
            --capabilities CAPABILITY_IAM
fi
