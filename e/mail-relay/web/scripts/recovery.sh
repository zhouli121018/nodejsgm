touch /tmp/trigger_file0
cp /usr/local/mail-relay/web/router_local.py /usr/local/mail-relay/web/router.py
cp /usr/local/mail-relay/web_customer/router_local.py /usr/local/mail-relay/web_customer/router.py
systemctl restart httpd.service
/usr/local/pyenv/versions/2.7.6/envs/relay/bin/supervisorctl -c /usr/local/mail-relay/control/conf/supervisor.conf restart all
rm /tmp/trigger_file0