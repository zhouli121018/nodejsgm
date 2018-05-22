#!/bin/sh
DATE=`/bin/date --date='1 day ago' +%Y-%m-%d`;
/usr/local/pythonbrew/venvs/Python-2.7.6/relay/bin/python /usr/local/mail-relay/control/statistics.py $DATE
