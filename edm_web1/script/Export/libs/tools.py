# -*- coding:utf-8 -*-

import re

P = re.compile('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$')

def validateEmail(addr):
    if P.match(addr):
        return True
    return False

# 检查是否是QQ地址
def validateQQ(addr):
    if addr.endswith("@qq.com") or addr.endswith("@vip.qq.com") or addr.endswith("@foxmail.com"):
        return True
    return False