#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import dns.resolver

dns.resolver.get_default_resolver().cache = dns.resolver.LRUCache()

import collections
import gevent.backdoor
import gevent.pool
import gevent.queue
import json
import random
import re
import smtplib
import socket
import time
import urllib3

from lib.core import config, log, get_redis_cli, get_message
from lib.model import ipv4_pattern
from lib.utility import address_domain, decode_msg

redis_cli = get_redis_cli()
http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=10, read=300))

state_dict = {}
pool = gevent.pool.Pool(config['greenlet_number'])
result = gevent.queue.Queue(10)


class State(object):
    __slots__ = ['domain', 'ip', 'queue', 'task_number']

    def __init__(self, domain, ip):
        self.domain = domain
        self.ip = ip
        self.queue = collections.deque()
        self.task_number = 0


class SMTP(smtplib.SMTP):
    def __init__(self, host, source_ip, local_hostname):
        self.source_ip = source_ip
        smtplib.SMTP.__init__(self, host=host, local_hostname=local_hostname)

    def _get_socket(self, host, port, timeout):
        return socket.create_connection((host, port), timeout, (self.source_ip, 0))

    def send_message(self, sender, receiver, message):
        code, msg = self.helo()
        if not (200 <= code <= 299):
            return code, msg

        code, msg = self.mail(sender)
        if code != 250:
            return code, msg

        code, msg = self.rcpt(receiver)
        if (code != 250) and (code != 251):
            return code, msg

        code, msg = self.data(message)
        return code, msg


def send(receive_ip, deliver_ip, helo, sender, receiver, message):
    try:
        try:
            with gevent.Timeout(config['connect_time']):
                s = SMTP(receive_ip, deliver_ip, helo)
        except gevent.Timeout:
            code, msg = -1, 'connect timeout'
        else:
            try:
                with gevent.Timeout(config['deliver_time']):
                    code, msg = s.send_message(sender, receiver, message)
            except gevent.Timeout:
                code, msg = -1, 'deliver timeout'
    except smtplib.SMTPResponseException as e:
        code, msg = e.smtp_code, e.smtp_error
    except BaseException as e:
        code, msg = -1, repr(e)
    return code, msg


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
        if re.match(ipv4_pattern, mx_domain):
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


def get_retry_state(return_code, return_message):
    url = 'http://{}:{}/retry_state/'.format(config['task']['host'], config['task']['port'])
    body = json.dumps({
        'return_code': return_code,
        'return_message': return_message
    })
    i = 0
    while True:
        try:
            r = http.urlopen('GET', url, body=body)
            if r.status == 200:
                return json.loads(r.data)['retry_state']
            else:
                log.warning(u'get_retry_state: fail, response={}'.format((r.status, r.reason)))
        except BaseException as e:
            log.warning(u'get_retry_state: error', exc_info=1)
        if i < 3:
            i += 1
            gevent.sleep(60)
        else:
            return True


def deliver(d):
    d['result'] = []
    try:
        mx_list = query_mx(address_domain(d['receiver']))
        if len(mx_list) == 0:
            d['result'].append({
                'deliver_time': time.time(),
                'mx_record': '',
                'receive_ip': '',
                'return_code': -1,
                'return_message': 'query mx failed'
            })
            return

        helo = redis_cli.hget('helo', d['deliver_ip']) or d['deliver_ip']
        message = get_message(d['mail_ident'])
        for mx_record, _, ip_list in mx_list:
            deliver_time = time.time()
            receive_ip = random.choice(ip_list)
            code, msg = send(receive_ip, d['deliver_ip'], helo, d['sender'], d['receiver'], message)
            msg = decode_msg(msg)
            d['result'].append({
                'deliver_time': deliver_time,
                'mx_record': mx_record,
                'receive_ip': receive_ip,
                'return_code': code,
                'return_message': msg
            })
            if code == 250:
                return
            if not get_retry_state(code, msg):
                return

    except BaseException as e:
        d['result'].append({
            'deliver_time': time.time(),
            'mx_record': '',
            'receive_ip': '',
            'return_code': -1,
            'return_message': repr(e)
        })

    finally:
        result.put(d)
        log.info(u'deliver: mail_ident={mail_ident}, sender={sender}, receiver={receiver}'.format(**d))


def put_one(ident):
    d = json.loads(redis_cli.hget('detail', ident))
    key = address_domain(d['receiver']), d['deliver_ip']
    if key not in state_dict:
        state_dict[key] = State(*key)
    state_dict[key].queue.appendleft(d)


def put_routine():
    for ident in reversed(redis_cli.lrange('waiting', 0, -1)):
        put_one(ident)
    while True:
        ident = redis_cli.brpoplpush('received', 'waiting')
        put_one(ident)


def get_routine():
    while True:
        l = [s for s in state_dict.itervalues()
             if len(s.queue) > 0 and
             s.task_number < 10]
        if len(l) > 0:
            s = random.choice(l)
            s.task_number += 1
            d = s.queue.pop()
            pool.spawn(deliver, d)
        else:
            gevent.sleep(1)


def result_routine():
    while True:
        d = result.get()

        key = address_domain(d['receiver']), d['deliver_ip']
        s = state_dict[key]
        s.task_number -= 1

        (redis_cli.pipeline()
         .lpush('delivered', d['mail_ident'])
         .lrem('waiting', 0, d['mail_ident'])
         .hset('detail', d['mail_ident'], json.dumps(d))
         .execute())


def main():
    global all_routine

    all_routine = [
        gevent.spawn(gevent.backdoor.BackdoorServer(('localhost', 10002)).serve_forever),
        gevent.spawn(put_routine),
        gevent.spawn(get_routine),
        gevent.spawn(result_routine)
    ]
    gevent.joinall(all_routine)


if __name__ == '__main__':
    main()
