# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#

import sys
import re
import signal
import traceback
import datetime
import gevent
from gevent.server import StreamServer
from gevent.monkey import patch_socket
import lib.common      as Common
from lib.common import outinfo, outerror


patch_socket()
Common.init_django_enev()

from apps.mail.models import TempSenderBlacklist


############################################################
# 公共数据

# 变量
_DEBUG = False
_SESSION_NAMES = {'rcpt': 'rule', 'end-of-message': 'size', '': 'unknow'}

############################################################
# “END-OF-MESSAGE”状态相关规则检测

class EOMProcessor(object):
    def __init__(self, ident, param):
        self.ident = ident

    # 运行处理器
    def run(self):
        return


############################################################
# “RCPT”状态相关规则检测

class RcptProcessor(object):
    def __init__(self, ident, param):
        # 任务基本信息
        self.ident = ident
        self.param = param
        self.client = param['client_address']
        self.recipient = param['recipient']


    # 运行处理器
    def run(self):
        self.sender = Tookit.bounce_address_process(self.param['sender'])
        if TempSenderBlacklist.objects.filter(sender=self.sender.lower(), expire_time__gte=datetime.datetime.now()):
            loginfo(self.ident, "TempSenderBlacklist from: %s, sender: %s, recipient: <%s>" % (
                self.client, self.sender, self.recipient
            ))
            return 'REJECT', 'sender in temp blacklist!'
        return


############################################################
# 工具类

class Tookit(object):
    # 发件人“退信地址验证”处理（Bounce Address Tag Validation）
    @staticmethod
    def bounce_address_process(addr):
        if addr[0:5] != 'prvs=': return addr
        return addr[addr.rindex('=') + 1:]


############################################################
# 主函数相关操作

# 接收策略检测参数
def receive_policy_param(file_object):
    params = {}

    # 接收传递过来的参数
    while True:
        line = file_object.readline()
        if len(line) == 0:
            return None
        line = line.strip()
        if not line: break
        # print line
        array = line.split('=', 1)
        if len(array) < 2: continue
        params[array[0]] = array[1]
        gevent.sleep(0)

    # 处理发件人参数
    if 'sender' not in params or not params['sender']:
        params['sender'] = 'unknown@unknown'

    # 处理收件人参数
    if 'recipient' in params and params['recipient']:
        params['recipient'] = params['recipient'].lower()

    return params


# 答复查询
def answer_query(file_object, action, message=None):
    full_data = 'action=%s' % action
    if message is not None: full_data += ' ' + message
    full_data += '\n\n'
    file_object.write(full_data)
    file_object.flush()


# 主处理函数
def main(client_socket, address):
    file_object = client_socket.makefile()

    while True:
        # 接收策略检测参数
        policy_param = receive_policy_param(file_object)
        if policy_param is None:
            break

        # 生成标识符
        if 'instance' in policy_param:
            ident = policy_param['instance']
        else:
            ident = Common.get_random_string(10)

        # 取得会话状态
        state = policy_param.get('protocol_state', '').lower()

        # 进行相关处理
        try:
            # 根据不同的状态调用不同的处理器
            if state == 'rcpt':
                processor = RcptProcessor(ident, policy_param)
                result = processor.run()
            elif state == 'end-of-message':
                processor = EOMProcessor(ident, policy_param)
                result = processor.run()
            else:
                result = None

            # 处理返回数据
            if result is None:
                r_action, r_message = 'DUNNO', None
            else:
                r_action, r_message = result
        except:
            logerror(ident, 'process exception\n%s' % traceback.format_exc())
            r_action, r_message = '451', 'program internal error'

        # 答复查询
        loginfo(ident, "%s: %s (%s)" % (_SESSION_NAMES[state], r_action, r_message))
        answer_query(file_object, r_action, r_message)


############################################################

# 信号量处理
def signal_handle(mode):
    outinfo("catch signal: %s" % mode)
    if mode != 'sigint': sys.exit(0)


# 日志打印
def loginfo(logid, msg):
    msg = u'[%s] %s' % (logid, msg)
    outinfo(msg)


def logerror(logid, msg):
    msg = u'[%s] %s' % (logid, msg)
    outerror(msg)


if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug()
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_pid_file('rulefilter.pid')
    Common.init_logger('RuleFilter', len(sys.argv) > 1, _DEBUG)

    # 运行服务
    EXIT_CODE = 0
    outinfo("program start")
    try:
        # 设置监听信号量
        gevent.signal(signal.SIGTERM, signal_handle, 'sigterm')
        gevent.signal(signal.SIGALRM, signal_handle, 'sigalrm')

        # 启动流服务器
        server = StreamServer(('127.0.0.1', 10026), main)
        server.serve_forever()

    except KeyboardInterrupt:
        signal_handle('sigint')
    except SystemExit, e:
        EXIT_CODE = e.code
    except:
        outerror(traceback.format_exc())
        EXIT_CODE = 1
    outinfo("program quit")
    sys.exit(EXIT_CODE)


