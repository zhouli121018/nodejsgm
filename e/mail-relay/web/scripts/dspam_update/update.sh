#!/bin/sh

#-----------------------------------------------------------
# 配置区

SAVE_PATH="/usr/local/mail-relay/web_customer/static/dspam";
RESOURCE_PATH="/usr/local/mail-relay/web/scripts/dspam_update";

DB_USER="postgres";
DB_PASS="MzdhYWU0MjJiY2NlMWNj";
DB_HOST="127.0.0.1";
DB_PORT=5432;
DB_DATABASE='dspam';


BIN_PSQL='/usr/pgsql-9.4/bin/psql';
BIN_PGDUMP='/usr/pgsql-9.4/bin/pg_dump';

#-----------------------------------------------------------
# 程序区

DATE=`/bin/date --date='1 day ago' +%Y-%m-%d`;
# 将数据导出
SQLFILE="${RESOURCE_PATH}/dump.sql";
TMPSQLFILE="${RESOURCE_PATH}/dump-tmp.sql";
echo $TMPSQLFILE;
rm -f "${TMPSQLFILE}";
cp "${SQLFILE}" "${TMPSQLFILE}";

perl -p -i -e "s/datetime/${DATE}/;" ${TMPSQLFILE};
rm /tmp/dspam.csv
#PGPASSWORD=$DB_PASS $BIN_PSQL -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_DATABASE -c "drop table dspam_token_data_tmp;"
#PGPASSWORD=$DB_PASS $BIN_PSQL -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_DATABASE -c "create table dspam_token_data_tmp as SELECT * FROM dspam_token_data where last_hit='$DATE';"
#PGPASSWORD=$DB_PASS $BIN_PGDUMP -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_DATABASE -t dspam_token_data_tmp -f /tmp/dspam_token_data.sql;
PGPASSWORD=$DB_PASS $BIN_PSQL -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_DATABASE -f ${TMPSQLFILE};
/usr/local/bin/7za a $SAVE_PATH/dspam_$DATE.7z /tmp/dspam.csv
find $SAVE_PATH -mtime 7 -exec rm {} \;

PGPASSWORD=$DB_PASS $BIN_PGDUMP -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_DATABASE | gzip > $SAVE_PATH/dspam_full.gz
