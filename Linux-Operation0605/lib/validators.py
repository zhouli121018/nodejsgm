# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

import re
from IPy import IP

# 判断 IP 或 IP段
P_IP = re.compile('^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
P_IPADDR = re.compile('^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\/(\d+)$')
def check_ipaddr(ip):
    if P_IP.match(ip):
        return True
    if P_IPADDR.match(ip):
        try:
            IP(ip)
            return True
        except:
            return False
    return False

# 判断 邮箱 或 域名
P_Email = re.compile('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$')
P_Domain = re.compile('^@\w+([-.]\w+)*\.(\w+)$')
def check_email_ordomain(email):
    if P_Email.match(email): return True
    if P_Domain.match(email): return True
    return False

# 域名 验证
def check_domain(domain):
    if P_Domain.match(domain): return True
    return False

# 只能填写英文字符！ 匹配英文字符 证书签名验证
P_EN = re.compile(ur'^[A-Za-z0-9!@#$%^&*~`\(\)_\-=+\\\|\}\]\[\{\'\"\;\:\/\?\>\.\<\,\s]+$')
# P_EN = re.compile('^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*~`\(\)_\-=+\\\|\}\]\[\{\'\"\;\:\/\?\>\.\<\,])[a-zA-Z\d!@#$%^&*~`\(\)_\-=+\\\|\}\]\[\{\'\"\;\:\/\?\>\.\<\,]{12,16}$')
def check_English(word):
    if P_EN.match(word): return True
    return False

def check_ip(ip):
    if P_IP.match(ip): return True
    return False

def check_email(email):
    if P_Email.match(email): return True
    return False
