#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ipaddress
import StringIO

from fabric.api import env, put, run
from fabric.contrib.files import append, contains, exists

ifcfg_template = '''\
DEVICE="{device}:{n}"
BOOTPROTO="none"
ONBOOT="yes"
NETMASK="{netmask}"
IPADDR="{ip}"
'''

supervisord_config_template = '''\
[unix_http_server]
file={work_dir}/run/supervisor.sock

[supervisord]
logfile={work_dir}/log/supervisord.log
logfile_maxbytes=10MB
logfile_backups=10
loglevel=info
pidfile={work_dir}/run/supervisord.pid
nodaemon=false
minfds=65536
minprocs=200

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://{work_dir}/run/supervisor.sock
'''

program_template = '''\
[program:{module}]
command                 = {python_prefix}/bin/python -m {package}.{module}
directory               = {work_dir}
autostart               = true
autorestart             = true
redirect_stderr         = true
stdout_logfile          = {work_dir}/log/{module}.log
stdout_logfile_maxbytes = 10MB
stdout_logfile_backups  = 10
environment             = PACKAGE_CONFIG="{work_dir}/etc/{package}.config"
'''

deliver_config_template = '''\
[redis]
host                = localhost
port                = 6379
db                  = 0

[task]
host                = {task_host}
port                = 10000

[deliver]
message_dir         = {work_dir}/message
greenlet_number     = 1000
connect_time        = 60
deliver_time        = 180
'''


# ------------------------------------------------
def pre_install():
    run('cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')

    if not exists('/var/swapfile'):
        run('dd if=/dev/zero of=/var/swapfile  bs=1M count=4096')
        run('mkswap /var/swapfile')
    s = '/var/swapfile swap swap defaults 0 0'
    if not contains('/etc/fstab', s):
        append('/etc/fstab', s)
    run('swapon -a')


def install_package():
    run('yum update -y')
    if not exists('/etc/yum.repos.d/epel.repo'):
        run('rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm')
    run('yum groupinstall -y Development')
    run('yum install -y bzip2-devel expat-devel gdbm-devel libffi-devel openssl-devel readline-devel sqlite-devel'
        ' zlib-devel postgresql-devel zeromq3-devel')
    run('yum install -y denyhosts dnsmasq redis bash-completion bind-utils nc ntp ntpdate openssh-clients rlwrap strace'
        ' telnet tmux emacs-nox vim-minimal')


def start_service():
    run('chkconfig denyhosts on')
    run('chkconfig dnsmasq on')
    run('chkconfig ntpd on')
    run('chkconfig redis on')
    run('service denyhosts start')
    run('service dnsmasq start')
    run('service ntpd start')
    run('service redis start')
    if exists('/etc/init.d/postfix'):
        run('chkconfig postfix off')
        run('service postfix stop')


def iptables_config():
    run('/sbin/iptables -F')
    run('/sbin/iptables -X')
    run('/sbin/iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT')
    run('/sbin/iptables -A INPUT -p icmp -j ACCEPT')
    run('/sbin/iptables -A INPUT -i lo -j ACCEPT')
    run('/sbin/iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT')
    run('/sbin/iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT')
    run('/sbin/iptables -A INPUT -p tcp -m tcp --dport 88 -j ACCEPT')
    run('/sbin/iptables -A INPUT -p tcp -m tcp --dport 10001 -j ACCEPT')
    run('/sbin/iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited')
    run('/sbin/iptables -A FORWARD -j REJECT --reject-with icmp-host-prohibited')
    run('service iptables save')


def create_pyenv(pyenv):
    """
    创建python虚拟环境

    Args:
        pyenv: string, 虚拟环境名称
    """

    if not exists('/usr/local/pyenv'):
        run('git clone https://github.com/yyuu/pyenv.git /usr/local/pyenv')
    if not exists('/usr/local/pyenv/plugins/pyenv-virtualenv'):
        run('git clone https://github.com/yyuu/pyenv-virtualenv.git /usr/local/pyenv/plugins/pyenv-virtualenv')
    if not exists('/usr/local/pyenv/versions/2.7.7/bin/python'):
        run('PYENV_ROOT=/usr/local/pyenv /usr/local/pyenv/bin/pyenv install -f 2.7.7')
    if not exists('/usr/local/pyenv/versions/{}/bin/python'.format(pyenv)):
        run('PYENV_ROOT=/usr/local/pyenv /usr/local/pyenv/bin/pyenv virtualenv -f 2.7.7 {}'.format(pyenv))
    run('PYENV_ROOT=/usr/local/pyenv /usr/local/pyenv/bin/pyenv rehash')


# ------------------------------------------------
def make_dir(work_dir):
    run('mkdir -p {}/etc'.format(work_dir))
    run('mkdir -p {}/log'.format(work_dir))
    run('mkdir -p {}/message'.format(work_dir))
    run('mkdir -p {}/run'.format(work_dir))


def copy_source(work_dir, source_path):
    run('rm -f {}/deliver.tar.gz'.format(work_dir))
    run('rm -rf {}/deliver'.format(work_dir))
    put(source_path, '{}/deliver.tar.gz'.format(work_dir))
    run('tar -C {0} -xf {0}/deliver.tar.gz'.format(work_dir))


def install_requirement(pip_path, requirements_file):
    run('{} install -r {}'.format(pip_path, requirements_file))


def supervisord_config(work_dir, pyenv, package, *modules):
    s = '\n'.join(
        [supervisord_config_template.format(work_dir=work_dir)] +
        [program_template.format(work_dir=work_dir, package=package, module=module,
                                 python_prefix='/usr/local/pyenv/versions/{}'.format(pyenv))
         for module in modules])
    put(StringIO.StringIO(s), '{}/etc/supervisord.conf'.format(work_dir))
    c = '/usr/local/pyenv/versions/{}/bin/supervisord -c {}/etc/supervisord.conf'.format(pyenv, work_dir)
    if not contains('/etc/rc.local', c):
        append('/etc/rc.local', c)


def deliver_config(work_dir, task_host):
    s = deliver_config_template.format(work_dir=work_dir, task_host=task_host)
    put(StringIO.StringIO(s), '{}/etc/deliver.config'.format(work_dir))


def ip_config(ip_list):
    run('rm -f /etc/sysconfig/network-scripts/ifcfg-eth*:*')
    run('service network restart')
    d = {}
    for i in ip_list:
        d.setdefault(i['device'], []).append(i)
    for device, l in d.items():
        l.sort(key=lambda i: ipaddress.ip_address(i['ip']))
        for n, i in enumerate(l):
            s = ifcfg_template.format(n=n, **i)
            put(StringIO.StringIO(s), '/etc/sysconfig/network-scripts/ifcfg-{}:{}'.format(device, n))
    for device, l in d.items():
        for n, i in enumerate(l):
            run('ifup {}:{}'.format(device, n))


def helo_config(ip_list):
    run('redis-cli DEL helo_tmp')
    run('redis-cli HMSET helo_tmp ' + ' '.join('{} {}'.format(i['ip'], i['helo']) for i in ip_list))
    run('redis-cli RENAME helo_tmp helo')


# ------------------------------------------------
def supervisord_start(work_dir, pyenv):
    if not exists('{}/run/supervisor.sock'.format(work_dir)):
        run('/usr/local/pyenv/versions/{}/bin/supervisord -c {}/etc/supervisord.conf'.format(pyenv, work_dir))
    else:
        run('/usr/local/pyenv/versions/{}/bin/supervisorctl -c {}/etc/supervisord.conf reload'.format(pyenv, work_dir))


# ------------------------------------------------
def deploy_deliver(host, port, user, password, source_path, task_host, ip_list):
    """
    完成所有部署工作
    """

    env.abort_on_prompts = True
    env.host_string = '{}@{}:{}'.format(user, host, port)
    env.password = password

    work_dir = '/usr/local/mailrelay-deliver'

    pre_install()
    install_package()
    start_service()
    iptables_config()

    create_pyenv('deliver')
    make_dir(work_dir)
    copy_source(work_dir, source_path)
    pip_path = '/usr/local/pyenv/versions/deliver/bin/pip'
    requirements_file = '{}/deliver/requirements.txt'.format(work_dir)
    install_requirement(pip_path, requirements_file)

    supervisord_config(work_dir, 'deliver', 'deliver', *['server', 'deliver', 'log'])
    deliver_config(work_dir, task_host)
    ip_config(ip_list)
    helo_config(ip_list)
    supervisord_start(work_dir, pyenv='deliver')


def update_source(host, port, user, password, source_path):
    """
    更新源代码并重启进程
    """

    env.abort_on_prompts = True
    env.host_string = '{}@{}:{}'.format(user, host, port)
    env.password = password

    work_dir = '/usr/local/mailrelay-deliver'

    copy_source(work_dir, source_path)
    pip_path = '/usr/local/pyenv/versions/deliver/bin/pip'
    requirements_file = '{}/deliver/requirements.txt'.format(work_dir)
    install_requirement(pip_path, requirements_file)
    supervisord_start(work_dir, pyenv='deliver')


def update_helo(host, port, user, password, ip_list):
    """
    更新 helo 配置
    """

    env.abort_on_prompts = True
    env.host_string = '{}@{}:{}'.format(user, host, port)
    env.password = password

    helo_config(ip_list)
