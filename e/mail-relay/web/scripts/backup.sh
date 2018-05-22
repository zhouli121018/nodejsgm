#!/usr/bin/sh

#备份过期的邮件详情表　如mail_20170501, cmail_20170501

EXT_DAYS=180 #　180以前的表进行备份
EXT_DAYS_END=$(expr $EXT_DAYS + 0)

SAVE_PATH="/home/backup"
DB_USER="postgres";
DB_PASS="MzdhYWU0MjJiY2NlMWNj";
DB_HOST="127.0.0.1";
DB_PORT=45600;
DB_DATABASE='mail-relay';

BIN_PSQL='/usr/pgsql-9.4/bin/psql';
BIN_PGDUMP='/usr/pgsql-9.4/bin/pg_dump';

#cat /home/backup/mail_20170501.gz | gunzip |PGPASSWORD=MzdhYWU0MjJiY2NlMWNj psql -U postgres -h 127.0.0.1 -p 45600 -d mail-relay

backup(){
    echo "backup $1";
    PGPASSWORD=$DB_PASS $BIN_PGDUMP -U $DB_USER -h $DB_HOST -p $DB_PORT -t $1 -d $DB_DATABASE | gzip > $SAVE_PATH/$1.gz
    PGPASSWORD=$DB_PASS $BIN_PSQL -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_DATABASE -c "DROP TABLE $1;"
}

for i in $(seq $EXT_DAYS $EXT_DAYS_END); do
    day=`date --date="${i} days ago" +%Y%m%d`;
    backup "mail_$day";
    backup "cmail_$day";
done;

