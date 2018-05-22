#!/usr/local/u-mail/python/bin/python
# -*-coding:utf8-*-
#

import os
import re
import json

import django
import sys
import fcntl
import datetime
import subprocess
import signal
import atexit
import time
import logging
import redis
import hashlib
from functools import wraps
from traceback import format_exc
from ConfigParser import ConfigParser
from HTMLParser import HTMLParser
import dns.resolver
from django.conf import settings


dns.resolver.get_default_resolver().cache = dns.resolver.LRUCache()



# ###########################################################
# 内部对象

# 常用路径

# APP相关路径
APP_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
APP_LOG_PATH = os.path.join(APP_ROOT, 'log')
APP_RUN_PATH = os.path.join(APP_ROOT, 'run')
APP_CONF_PATH = os.path.join(APP_ROOT, 'conf')


# 配置对象
cfgDefault = None

# ###########################################################
# 日志输出相关函数

# 日志输出函数
def outinfo(msg): outlog(msg, logging.INFO)


def outerror(msg): outlog(msg, logging.ERROR)


def outdebug(msg): outlog(msg, logging.DEBUG)


def outlog(m, t): logging.log(t, m)


############################################################
# 应用程序环境初始化

def check_debug(index=1):
    if len(sys.argv) > index and sys.argv[index] == 'debug':
        return True
    return False


def init_run_user(user):
    run_user_name = get_system_user_name()
    if run_user_name not in [user, 'root']:
        outerror('Error: please use {} or "root" user runing!'.format(user))
        sys.exit(-1)
    if run_user_name == 'root':
        os.setgid(get_system_group_id(user))
        os.setuid(get_system_user_id(user))
    return True


def init_pid_file(filename):
    def _clear_pidfile(_pidfile):
        if not os.path.exists(_pidfile): return
        try:
            os.unlink(_pidfile)
        except:
            pass

    pidfile = os.path.join(APP_RUN_PATH, filename)
    try:
        fd = os.open(pidfile, os.O_RDWR | os.O_CREAT | os.O_NONBLOCK | os.O_DSYNC, 0644)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.write(fd, str(os.getpid()))
        atexit.register(_clear_pidfile, pidfile)
    except IOError:
        print >> sys.stderr, "Error: program is already running!"
        sys.exit(-2)
    except OSError, e:
        print >> sys.stderr, "Error: %s" % e
        sys.exit(-2)
    return True


def init_logger(name, onscreen=True, debug=False, stdout=True, user=None):
    """
    初始化日志记录模块
    :param name: 应用程序标识符，字符串
    :param onscreen: 是否要将日志在屏幕上显示，布尔类型
    :param debug: 是否为调试模式，布尔类型
    :param stdout: 是否重定向系统标准输出，布尔类型
    :param user: 记录日志的用户
    :return: bool
    """
    import Logger

    level = logging.DEBUG if debug else logging.INFO

    # 设置日志文件
    if name is None: name = 'default'
    if not os.path.exists(APP_LOG_PATH) or not _is_writable(APP_LOG_PATH):
        print >> sys.stderr, 'Error: no have log path write permission!'
        sys.exit(1)
    log_file = os.path.join(APP_LOG_PATH, name.lower() + '.log')
    err_file = os.path.join(APP_LOG_PATH, 'error.log')

    # 检测日志文件写权限
    if ( os.path.exists(log_file) and not _is_writable(log_file) ) or (
                os.path.exists(err_file) and not _is_writable(err_file) ):
        print >> sys.stderr, 'Error: no have logfile write permission!'
        sys.exit(1)

    # 初始化日志记录器
    file_owner_uid = get_system_user_id(user)
    Logger.init_logger(name, log_file, err_file, level, (file_owner_uid, None))

    # 移除屏幕输出
    if not onscreen: Logger.remove_screen_output()

    # 重定向系统标准输出
    if stdout: Logger.redirect_stdout()
    return True


def init_cfg_default():
    if cfgDefault is not None: return
    globals()['cfgDefault'] = make_config_object(os.path.join(APP_CONF_PATH, 'config.conf'))


############################################################
# 程序运行基础函数

# 取得指定 UID 的用户名，如果未指定 UID 则使用当前运行用户的 UID
def get_system_user_name(uid=None):
    from pwd import getpwuid

    if uid is None: uid = os.getuid()
    return getpwuid(uid)[0]


# 根据指定的用户名取得对应的 UID, 如果未指定, 则返回当前运行用户的 UID
def get_system_user_id(uname=None):
    from pwd import getpwnam

    if uname is None:
        return os.getuid

    return getpwnam(uname)[2]


# 根据指定的用户名取得对应的 UID, 如果未指定, 则返回当前运行用户的 UID
def get_system_group_id(uname=None):
    from pwd import getpwnam

    if uname is None:
        return os.getuid

    return getpwnam(uname)[3]


# 检测对指定文件、路径是否有写权限
def _is_writable(path):
    return os.access(path, os.W_OK)


# 设置程序结束信号量
def signal_init(handler):
    import signal

    signal.signal(signal.SIGINT, handler)  # 处理 Ctrl-C
    signal.signal(signal.SIGTERM, handler)  # 处理 kill
    signal.signal(signal.SIGALRM, handler)  # 处理 signal.alarm()


# 设置程序结束信号量
def gevent_signal_init(handler):
    import gevent, signal

    gevent.signal(signal.SIGINT, handler, 'sigint')  # 处理 Ctrl-C
    gevent.signal(signal.SIGTERM, handler, 'sigterm')  # 处理 kill
    gevent.signal(signal.SIGALRM, handler, 'sigalrm')  # 处理 signal.alarm()


############################################################
# 常用函数

# 创建配置文件对象
def make_config_object(file_path):
    p = ConfigParser()
    p.read(file_path)
    return p


# 安全调用对象
def safe_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        outerror('call "%s" failure\n%s' % (fn.__name__, format_exc()))
        return None


# 等待调用成功 (有超时时间)
def time_call(fn, *args, **kwargs):
    try_count = 3
    while try_count > 0:
        res = safe_call(fn, *args, **kwargs)
        if res is not None: return res
        outerror('try call "%s" count: %d' % (fn.__name__, try_count))
        try_count -= 1
        time.sleep(2)
    return


# 等待调用成功 (无超时时间)
def wait_call(fn, *args, **kwargs):
    while True:
        res = time_call(fn, *args, **kwargs)
        if res is not None: return res
        time.sleep(1)
    return


# 竞争锁调用对象
def lock_call(lock, fn, *args, **kwargs):
    with lock:
        return fn(*args, **kwargs)


# 创建指定的多个路径
def make_dir(path_list, permit=0755):
    if type(path_list) != type([]): path_list = [path_list]
    for path in path_list:
        if os.path.exists(path): continue
        recursion_make_dir(path, permit)
    return True


def init_makedir():
    make_dir([APP_RUN_PATH, APP_LOG_PATH])


# 递归创建路径
def recursion_make_dir(path, permit=0755):
    if path[0] != '/': return False
    path_list = os.path.realpath(path).split('/')[1:]
    path_full = ''
    for item in path_list:
        path_full += '/' + item
        if os.path.exists(path_full): continue
        os.mkdir(path_full)
        os.chmod(path_full, permit)
    return True


# 生成插入 SQL 语句
def build_insert_sql(tbname, data):
    field_list = data.keys()
    placeholder = ['%s'] * len(field_list)
    sql = "INSERT INTO `%s` (`%s`) VALUES (%s)" % (
        tbname, '`, `'.join(field_list), ', '.join(placeholder)
    )
    return sql, data.values()


# 生成更新 SQL 语句
def build_update_sql(tbname, data, where='1', param=None):
    if param is None: param = []
    field_list = data.keys()
    value_list = data.values()
    sql = "UPDATE `%s` SET `%s`=%%s WHERE %s" % (
        tbname, '`=%s, `'.join(field_list), where
    )
    return sql, value_list + param


############################################################
#导入django环境
def init_django_enev(setting_file='web.settings'):
    web_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../web'))
    sys.path.append(web_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", setting_file)
    if django.VERSION >= (1, 7):
        django.setup()


def get_redis_cli():
    if cfgDefault is None:
        init_cfg_default()

    return redis.StrictRedis(
        host=cfgDefault.get('redis', 'host'),
        port=cfgDefault.getint('redis', 'port'),
        db=cfgDefault.getint('redis', 'db'),
        password=cfgDefault.get('redis', 'password')
    )


def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.func_name, str(t1 - t0))
        )
        return result

    return function_timer


def high_light(s, light_str):
    return s.replace(light_str,
                     u'<span style="background-color: yellow"><b style="color:#A94442;">{}</b></span>'.format(
                         light_str)) if s else ''


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def shell_escape_str(str):
    """
    处理shell转义单引号
    :param str:
    :return:
    """
    return str.replace("'", "'\''")


def timeout_command(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while process.poll() is None:
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            try:
                os.kill(process.pid, signal.SIGKILL)
            except OSError:
                pass
            os.waitpid(-1, os.WNOHANG)
            return ''
        time.sleep(0.2)
    return process.stdout.readlines()


def my_grep(file_name, grep_list):
    with open(file_name, 'r') as f:
        num = 0
        for line in f:
            for g in grep_list:
                g = g.encode('ascii')
                if line.find(g) == -1:
                    break
            else:
                num += 1
    return num


def my_grep1(file_name, grep_list, limit=0):
    res = []
    with open(file_name, 'r') as f:
        num = 0
        for line in f:
            for g in grep_list:
                g = g.encode('ascii')
                if line.find(g) == -1:
                    break
            else:
                res.append(line)
                num += 1
            if limit and num >= limit:
                break
    return num, res


def get_date(data):
    date = data.get('date', '')
    if not date:
        date = time.strftime('%Y%m%d')
    else:
        date = date.replace('-', '')
    return date


def scp(file_path, host, port, flat=True):
    """
    scp 文件到本地
    :param file_path: 文件路径
    :param host:
    :param port:
    :param flat: True为file在host上，　需scp到本地
    　　　　　　　False为file在本地，　需scp到服务器上
    :return:
    """
    kwargs = {
        'file_path': file_path,
        'host': host,
        'port': port,
    }
    if flat:
        cmd = "sudo scp -P {port} root@{host}:{file_path} {file_path}".format(**kwargs)
    else:
        cmd = "scp -P {port} {file_path} root@{host}:{file_path}".format(**kwargs)
    safe_call(timeout_command, cmd, 60)


def safe_format(template, **kwargs):
    def replace(mo):
        name = mo.group('name')
        if name in kwargs:
            return unicode(kwargs[name])
        else:
            return mo.group()

    p = r'\{(?P<name>\w+)\}'
    return re.sub(p, replace, template)


def try_query(qname, rdtype):
    try:
        return dns.resolver.query(qname, rdtype)
    except dns.exception.DNSException:
        return []


def query_mx(domain):
    """
    查询 mx 记录
    返回 mx 记录, 优先级, ip_list 组成的 tuple 的 list, 按优先级排序.

    兼容性:
    mx 纪录直接到 ip.
    mx 不存在,用 a 记录替代.
    """

    mx_list = []
    for a in try_query(domain, 'mx'):
        mx_domain = str(a.exchange).strip('.')
        if mx_domain:
            mx_list.append((mx_domain, a.preference, [mx_domain]))
        else:
            l = [str(b) for b in try_query(mx_domain, 'a')]
            if len(l) > 0:
                mx_list.append((mx_domain, a.preference, l))

    if len(mx_list) > 0:
        mx_list.sort(key=lambda x: x[1])
        return mx_list

    l = [str(b) for b in try_query(domain, 'a')]
    if len(l) > 0:
        return [(domain, 10, l)]

    return []


class ComplexEncoder(json.JSONEncoder):
    """json扩展，让它可以支持datetime类型"""

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def get_file_count(file_path, seconds=86400):
    """
    获取目录file_path下 days天数内创建的文件数量
    :param file_path:
    :param days:
    :return:
    """
    return len(
        filter(lambda f: os.stat(os.path.join(file_path, f)).st_atime + seconds > time.time(), os.listdir(file_path)))

def get_auth_key():
    auth_key = settings.AUTH_KEY
    return hashlib.md5('%s-%s' % (auth_key, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()
