# -*- coding: utf-8 -*-
#
'''
http://blog.csdn.net/u011628250/article/details/73526390
'''

import os
import time
import socket
import dns.resolver
from functools import wraps
ROOT = os.path.realpath(os.path.split(__file__)[0])
resolv_file = os.path.join(ROOT, '..', 'conf', 'resolv.conf')
dns.resolver.default_resolver = dns.resolver.Resolver(filename=resolv_file)
dns.resolver.get_default_resolver().cache = dns.resolver.LRUCache()
from .log import log

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = time.time()
        ret = func(*args, **kwargs)
        T = int( (time.time() - t) *1000 )
        return ret, T
    return wrapper

# dns反向解析，根据ip获得域名方法
def get_hostname(ip):
    try:
        result = socket.gethostbyaddr(ip)
        return result[0]
        # Display the list of available addresses that is also returned
        # print '\nAddresses:'
        # for item in result[2]:
        #     print '  ' + item
    except socket.herror, e:
        # log.error(traceback.format_exc())
        return None

################################################
# RDNS
@timeit
def RDnsQuery(ip, domain=None, answers=None, rdtype="a"):
    if isinstance(answers, basestring):
        answers = [answers]
    reversed_ip = '.'.join(reversed(ip.split('.')))
    try:
        r = dns.resolver.query('{}.{}'.format(reversed_ip, domain), rdtype)
    except dns.resolver.NXDOMAIN:
        r = []
    except BaseException as e:
        log.error('RDnsQuery error: ip={}, domain: {}, error: {}'.format(ip, domain, e))
        # log.error(traceback.format_exc())
        return False
    for i in r:
        i = str(i)
        if i in answers:
            return True
        else:
            log.warning('RDnsQuery error: ip={} results={}'.format(ip, list(r)))
    return False


def show_ret(ip, ret, tm, desc=None):
    if ret:
        msg = "IP {} is blacklisted!- {}({}ms) ".format(ip, desc, tm)
        status = True
    else:
        msg = "IP {} is not listed.- {}({}ms)".format(ip, desc, tm)
        status = False
    return status, msg