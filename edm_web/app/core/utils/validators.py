# -*- coding: utf-8 -*-
#
import re

# 检测 域名格式
domain_regex = re.compile('^\w+([-.]\w+)*\.(\w+)$')
def check_domains(domain):
    if domain_regex.match(domain): return True
    return False

