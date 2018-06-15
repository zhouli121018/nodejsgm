# -*- coding:utf-8 -*-

# 检查是否是QQ地址
def check_qq_addr(addr):
    if addr.endswith("@qq.com") or addr.endswith("@vip.qq.com") or addr.endswith("@foxmail.com"):
        return True
    return False