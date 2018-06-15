# -*- coding: utf-8 -*-
#

import re
import sys
import time
import string
import traceback

LETTERS_AND_DIGITS = string.ascii_letters + string.digits

# 自定义错误
class MyExceptionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# 字符串替换
def safe_format(template, **kwargs):
    def replace(mo):
        name = mo.group('name')
        if name in kwargs:
            return unicode(kwargs[name])
        else:
            return mo.group()

    p = r'\{(?P<name>\w+)\}'
    return re.sub(p, replace, template)

############################################################
# 安全调用对象
def safe_call(fn, *args, **kwargs):
    try :
        return fn(*args, **kwargs)
    except Exception, e:
        # sys.stderr.write('call "%s" failure\n %s' % (fn.__name__, e.message))
        # sys.stderr.write(traceback.format_exc())
        print >>sys.stderr, 'call "%s" failure\n %s' % (fn.__name__, e.message)
        print >>sys.stderr, traceback.format_exc()
        return None

# 等待调用成功 (有超时时间)
def time_call(fn, *args, **kwargs):
    try_count=3
    while try_count > 0 :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        print >>sys.stderr, 'try call "%s" count: %d' % (fn.__name__, try_count)
        # sys.stderr.write('try call "%s" count: %d' % (fn.__name__, try_count))
        try_count -= 1
        time.sleep(3)
    return

# 等待调用成功 (无超时时间)
def wait_call(fn, *args, **kwargs):
    while True :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        time.sleep(3)
    return

if __name__ == "__main__":
    import datetime
    kwargs = {}
    kwargs.update(
        COMPANY=u'深圳市安般科技有限公司', NAME=u'Allen',
        TIME=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), AREA=u'深圳福田',
        POINT=100, DOMAIN=u'test.com',
        TASK='', LAVE='',
    )
    template = u'尊敬的{COMPANY} ，贵司账号在{AREA}登陆U-Mail营销系统，如果不是授权行为，请及时修改密码和检查微信绑定账号！\n有任何疑问请致电400-8181-568，我们将竭诚为您服务！'
    template = safe_format(template, **kwargs)
    print template

