#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO

from fabric.api import env, put, run
from fabric.contrib.files import append, contains, exists

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
[program:{package}_{module}]
command                 = {python_prefix}/bin/python -m {package}.{module}
directory               = {work_dir}
autostart               = true
autorestart             = true
redirect_stderr         = true
stdout_logfile          = {work_dir}/log/{module}.log
stdout_logfile_maxbytes = 100MB
stdout_logfile_backups  = 10
environment             = PYTHONPATH="{work_dir}/ttt", PACKAGE_CONFIG="{work_dir}/etc/{package}.config"
'''

program_template_1 = '''\
[program:{package}_{module}]
command                 = {python_prefix}/bin/python {path}{args}
directory               = {work_dir}
autostart               = true
autorestart             = true
redirect_stderr         = true
stdout_logfile          = {work_dir}/log/{module}.log
stdout_logfile_maxbytes = 100MB
stdout_logfile_backups  = 10
'''

task_les_config_template = '''\
[redis]
host                = 127.0.0.1
port                = 6379
db                  = 0

[postgres]
host                = 127.0.0.1
port                = 5432
database            = mm-log
user                = mm-log
password            = ******

[mysql]
host                = 127.0.0.1
port                = 3306
db                  = mm-ms
user                = edm_web
passwd              = ******

[task]
server_address      = 0.0.0.0
server_port         = {task_port}
message_dir         = /usr/local/mm-bs/data/mails-default
'''

program_list = [
    'edm_app/src/wc_dispatcher',
    'edm_app/web_api/server',
    'mm-bs/bin/channel_chk.py',
    'mm-bs/src/assign_address',
    'mm-bs/src/bs_esmtpd',
    'mm-bs/src/handle_mails',
    'mm-bs/src/smtpsender',
    'mm-bs/src/split_mails',
    'mm-bs/src/sync_redis',
    'mm-bs/src/testallocator',
    'mm-bs/web_api/server',
    'mm-log/bin/logmonitor',
    'zhi_meng/manage runserver 0.0.0.0:8888'
]


# ------------------------------------------------
def install_package():
    if not exists('/etc/yum.repos.d/epel.repo'):
        run('rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm')
    run('yum groupinstall -y Development')
    run('yum install -y bzip2-devel expat-devel gdbm-devel libffi-devel openssl-devel readline-devel sqlite-devel'
        ' zlib-devel postgresql-devel zeromq3-devel')
    run('yum install -y denyhosts dnsmasq redis bash-completion bind-utils nc ntpdate openssh-clients rlwrap strace'
        ' telnet tmux emacs-nox vim-minimal')


def set_datetime():
    try:
        run('cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
        run('ntpdate pool.ntp.org')
        run('hwclock -w')
    except:
        pass


def start_service():
    run('chkconfig denyhosts on')
    run('chkconfig dnsmasq on')
    run('chkconfig redis on')
    run('service denyhosts start')
    run('service dnsmasq start')
    run('service redis start')


def create_pyenv(pyenv):
    if not exists('/usr/local/pyenv'):
        run('git clone https://github.com/yyuu/pyenv.git /usr/local/pyenv')
    if not exists('/usr/local/pyenv/plugins/pyenv-virtualenv'):
        run('git clone https://github.com/yyuu/pyenv-virtualenv.git /usr/local/pyenv/plugins/pyenv-virtualenv')
    if not exists('/usr/local/pyenv/versions/2.7.11/bin/python'):
        run('PYENV_ROOT=/usr/local/pyenv /usr/local/pyenv/bin/pyenv install -f 2.7.11')
    if not exists('/usr/local/pyenv/versions/{}/bin/python'.format(pyenv)):
        run('PYENV_ROOT=/usr/local/pyenv /usr/local/pyenv/bin/pyenv virtualenv -f 2.7.11 {}'.format(pyenv))
    run('PYENV_ROOT=/usr/local/pyenv /usr/local/pyenv/bin/pyenv rehash')


# ------------------------------------------------
def make_dir(work_dir):
    run('mkdir -p {}/etc'.format(work_dir))
    run('mkdir -p {}/log'.format(work_dir))
    run('mkdir -p {}/message'.format(work_dir))
    run('mkdir -p {}/run'.format(work_dir))


def copy_source(base_dir, source_path):
    put(source_path, '{}/lo.tar.gz'.format(base_dir))
    run('tar -C {0} -xf {0}/lo.tar.gz'.format(base_dir))


def install_requirement(pyenv, file):
    run('/usr/local/pyenv/versions/{}/bin/pip install -r {}'.format(pyenv, file))


def supervisord_config(base_dir, work_dir, pyenv):
    l = [supervisord_config_template.format(work_dir=work_dir)]
    for module in ['dispatch', 'server']:
        l.append(program_template.format(
            package='task_les',
            module=module,
            python_prefix='/usr/local/pyenv/versions/{}'.format(pyenv),
            work_dir=work_dir
        ))
    for p in program_list:
        i = p.find(' ')
        if i >= 0:
            path = p[:i]
            args = p[i:]
        else:
            path = p
            args = ''
        sp = path.split('/')
        run('mkdir -p {}/{}/log'.format(base_dir, sp[0]))
        l.append(program_template_1.format(
            package=sp[0],
            module=sp[-1],
            python_prefix='/usr/local/pyenv/versions/{}'.format(pyenv),
            work_dir='{}/{}'.format(base_dir, sp[0]),
            path='{}/{}.pyc'.format(base_dir, path),
            args=args))
    put(StringIO.StringIO('\n'.join(l)), '{}/etc/supervisord.conf'.format(work_dir))
    c = '/usr/local/pyenv/versions/{}/bin/supervisord -c {}/etc/supervisord.conf'.format(pyenv, work_dir)
    if not contains('/etc/rc.local', c):
        append('/etc/rc.local', c)


def task_les_config(work_dir, task_port):
    s = task_les_config_template.format(work_dir=work_dir, task_port=task_port)
    put(StringIO.StringIO(s), '{}/etc/task_les.config'.format(work_dir))


# ------------------------------------------------
def supervisord_start(work_dir, pyenv):
    if not exists('{}/run/supervisor.sock'.format(work_dir)):
        run('/usr/local/pyenv/versions/{}/bin/supervisord -c {}/etc/supervisord.conf'.format(pyenv, work_dir))
    else:
        run('/usr/local/pyenv/versions/{}/bin/supervisorctl -c {}/etc/supervisord.conf reload'.format(pyenv, work_dir))


# ------------------------------------------------
def deploy_task(host, port, user, password, base_dir, source_path):
    env.abort_on_prompts = True
    env.host_string = '{}@{}:{}'.format(user, host, port)
    env.password = password

    pyenv = 'relay'
    work_dir = '{}/mail-relay'.format(base_dir)

    install_package()
    set_datetime()
    start_service()
    create_pyenv(pyenv)

    install_requirement(pyenv, '{}/requirements_all.txt'.format(work_dir))


deploy_task('127.0.0.1', 22, 'root', '***', '/usr/local', '/opt/lo/lo.tar.gz')

