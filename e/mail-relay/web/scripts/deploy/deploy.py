# coding=utf-8
import os
import sys
import logging
import logging.handlers
import traceback
from datetime import datetime

ROOT = os.path.realpath(os.path.split(__file__)[0])

sys.path.append(os.path.join(ROOT, '..', '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
import django
# sys.path.append(web_path)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
if django.VERSION >= (1,7):
    django.setup()


from apps.core.models import Cluster, ClusterIp
from lib import pidfile, tools
from django.conf import settings

log = None

def set_logger(log_file, is_screen=True):
    global log
    log = logging.getLogger('deploy')
    log.setLevel(logging.INFO)
    format = logging.Formatter('%(asctime)-15s %(levelname)s %(message)s')

    log_handler = logging.handlers.RotatingFileHandler(log_file, 'a', 20000000, 4)
    # log_handler = logging.FileHandler(log_file)
    log_handler.setFormatter(format)
    log.addHandler(log_handler)
    sys.stdout = open(log_file, 'a')

    if is_screen:
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(format)
        log.addHandler(log_handler)


def change_deploy_status(c, status):
    c.deploy_status = status
    c.deploy_dtm = datetime.now()
    c.save()


def deploy_deliver(cluster_id):
    import fabfile

    clusters = Cluster.objects.filter(id=cluster_id)
    if not clusters:
        log.error('no cluster')
        sys.exit(1)
    log.info('start deploying')

    c = clusters[0]
    host = c.ip
    port = c.port
    user = c.username
    password = c.password

    ip_list = [{'ip': unicode(i.ip), 'device': i.device, 'netmask': i.netmask, 'helo': i.helo}
               for i in ClusterIp.objects.filter(cluster_id=cluster_id)]

    task_host = settings.ALLOWED_HOSTS[0]


    source_path = '/usr/local/mail-relay/deliver.tar.gz'

    try:
        if c.deploy_status == 'deploying':
            fabfile.deploy_deliver(host, port, user, password, source_path, task_host, ip_list)
        else:
            fabfile.update_helo(host, port, user, password, ip_list)
        change_deploy_status(c, 'success')
        log.info('deploy successful')
    except:
        change_deploy_status(c, 'fail')
        log.error('deploy failed')
        log.error(traceback.format_exc())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Error: lack of param"
        sys.exit(1)

    # 接收参数
    cluster_id = sys.argv[1]

    if not cluster_id.isdigit():
        print "Error: param error"
        sys.exit(1)

    log_dir = os.path.join(ROOT, 'log')
    pid_dir = os.path.join(ROOT, 'pid')
    log_file = os.path.join(log_dir, 'deploy_%s.log' % cluster_id)
    pid_file = os.path.join(pid_dir, 'deploy_%s.pid' % cluster_id)
    tools.make_dir([log_dir, pid_dir])

    set_logger(log_file)
    pidfile.register_pidfile(pid_file)
    deploy_deliver(cluster_id)
