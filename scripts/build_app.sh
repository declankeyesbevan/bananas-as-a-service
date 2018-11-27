#!/usr/bin/env bash

rm -rf build/*
virtualenv build/env
. build/env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -t build
cp -r bananas_as_a_service build
deactivate
rm -rf build/env
