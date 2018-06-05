#!/bin/sh

rm -rf /tmp/operation
mkdir /tmp/operation
git archive --format zip --output /tmp/operation/operation.zip master
unzip -d /tmp/operation /tmp/operation/operation.zip
rm /tmp/operation/operation.zip

/usr/local/u-mail/app/engine/bin/python -m compileall -f /tmp/operation
#/home/comingchina/.pythonbrew/venvs/Python-2.7.6/ope/bin/python -m compileall -f /tmp/operation
find /tmp/operation -name "*.py" -exec rm {} \;
