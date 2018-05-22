# !/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncore
import base64
import socket
import smtpd
import traceback
import uuid
import os
import sys
import signal
import time

import lib.common as Common


Common.init_django_enev()
from django.conf import settings
# from redis_cache import get_redis_connection
from lib.django_redis import get_redis
from django.db import connection

smtpd.__version__ = "ESMTP READY"

from lib.validators import *

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('bs_esmtpd')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)


# ###########################################################
# 公共数据

received_template = '''Received: from {helo} (unknown [{ip}])\n by {host} (Postfix) with ESMTP id {mail_id}\n for <{mailfrom}>; {date}\n'''
plain_pattern = re.compile(r'^[^\x00]*\x00([^\x00]+)\x00([^\x00]*)$')
stat_reject_key = 'bs:stat_reject:{uid}:{date}'

_DEBUG = False
redis_db = None
# ###########################################################

def handle_exit(*args, **kw):
    log.info('emstpd(pid=%s) exited' % os.getpid())
    sys.exit()


def kill_children(*args, **kw):
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGCHLD, handle_exit)
    os.killpg(os.getpgid(os.getpid()), signal.SIGINT)


class SMTPChannel(smtpd.SMTPChannel):
    def __init__(self, server, conn, addr, user_validator=None, ip_validator=None, domain_validator=None, collect_domain_validator=None):
        smtpd.SMTPChannel.__init__(self, server, conn, addr)
        self.username = None
        self.password = None
        self.uid = None
        self.auth_method = None
        self.domain_validator = domain_validator
        self.collect_domain_validator = collect_domain_validator

        self.authenticating = False
        self.authenticated = False
        #代收收件人列表
        self.__collect_rcpttos = {}

        disabled, uid = ip_validator(addr[0])
        if disabled == '0':
            self.uid = uid
            self.user_validator = None
            self.authenticated = True
        else:
            self.user_validator = user_validator


    def handle_error(self):
        log.error(traceback.format_exc())
        self.handle_close()


    def smtp_EHLO(self, arg):
        if not arg:
            self.push('501 Syntax: HELO hostname')
            return
        if self.__greeting:
            self.push('503 Duplicate HELO/EHLO')
        else:
            self.__greeting = arg
            self.push('250-%s Hello %s' % (self.__fqdn, arg))
            #self.push('250-AUTH PLAIN LOGIN CRAM-MD5 DIGEST-MD5')
            self.push('250-AUTH PLAIN LOGIN')
            self.push('250 EHLO')


    def smtp_MAIL(self, arg):
        address = self.__getaddr('FROM:', arg) if arg else None
        if not address:
            self.push('501 Syntax: MAIL FROM:<address>')
            return
        if self.__mailfrom:
            self.push('503 Error: nested MAIL command')
            return
        if self.username and self.username != address:
            self.push('503 Error: invalid from address: %s' % address)
            return
        # if not check_email_format(address):
        #     self.push('503 Error: from address format invalid')
        #     return

        #信任域名验证
        if not self.authenticated:
            disabled, uid = self.domain_validator(address.split('@')[-1])
            if disabled == '0':
                self.uid = uid
                self.user_validator = None
                self.authenticated = True

        self.__mailfrom = address
        self.push('250 Ok')


    def smtp_RCPT(self, arg):
        if not self.__mailfrom:
            self.push('503 Error: need MAIL command')
            return
        address = self.__getaddr('TO:', arg) if arg else None
        if not address:
            self.push('501 Syntax: RCPT TO: <address>')
            return

        disabled, uid = self.collect_domain_validator(address.split('@')[-1])
        if disabled == '0':
            self.__collect_rcpttos.setdefault(uid, []).append(address)
            self.push('250 Ok')
            return

        # date = datetime.date.today().strftime('%Y-%m-%d')
        # redis_key = stat_reject_key.format(uid=self.uid, date=date)

        # if not check_email_format(address):
        #     self.push('503 Error: address format invalid')
        #     redis_db.hincrby(redis_key, 'count_err_9', 1)
        #     format: 'task_id customer_id send_date error_type sender recipient'
            # redis_db.rpush('bs:stat_error_list', '%s,%s,%s,%s,%s,%s' % (0, self.uid, date, 9, self.__mailfrom, address))
            # return
        if self.authenticated:
            self.__rcpttos.append(address)
            self.push('250 Ok')
            return
        self.push('454 ERROR: Relay access denied')



    def smtp_AUTH(self, arg):
        split_args = arg.strip().split(' ')
        if not self.auth_method:
            self.auth_method = split_args[0].upper()

        if self.auth_method == 'PLAIN':
            if len(split_args) == 2:
                plain_auth = split_args[1]
                matched = plain_pattern.search(base64.b64decode(plain_auth))
                if matched:
                    self.username, self.password = matched.groups()

            elif self.authenticating:
                plain_auth = arg
                matched = plain_pattern.search(base64.b64decode(plain_auth))
                if matched:
                    self.username, self.password = matched.groups()

        elif self.auth_method == 'LOGIN':
            if self.username:
                self.password = base64.b64decode(arg)
            elif len(split_args) == 2:
                self.username = base64.b64decode(arg.split(' ')[1])
                self.push('334 ' + base64.b64encode('Password:'))
            elif self.authenticating and not self.username:
                self.username = base64.b64decode(arg)
                self.push('334 ' + base64.b64encode('Password:'))
            else:
                self.push('334 ' + base64.b64encode('Username:'))

        else:
            self.push('535 Not support auth method: %s ' % self.auth_method)
            self.authenticating = False
            log.error('not support auth method: %s, ip=%s' % (self.auth_method, self.addr))

        self.authenticating = True

        if self.username and self.password:
            self.authenticating = False

            if not self.user_validator:
                self.authenticated = True
                self.push('235 Authentication successful.')
                return

            disabled, uid = self.user_validator(self.username, self.password)
            if disabled == '0':
                self.authenticated = True
                self.uid = uid
                self.push('235 Authentication successful.')

            elif disabled == '1':
                log.info('user disabled: %s' % self.username)
                self.push('454 User disabled')

            else:
                log.info('authentication failure: %s' % self.username)
                self.push('454 Authentication failure')

    def smtp_DATA(self, arg):
        if not self.__rcpttos and not self.__collect_rcpttos:
            self.push('503 Error: need RCPT command')
            return
        if arg:
            self.push('501 Syntax: DATA')
            return
        self.__state = self.DATA
        self.set_terminator('\r\n.\r\n')
        self.push('354 End data with <CR><LF>.<CR><LF>')


    """
    def smtp_DATA(self, arg):
        if not self.__rcpttos:
            self.push('503 Error: need RCPT command')
            return
        if arg:
            self.push('501 Syntax: DATA')
            return
        if not self.authenticated:
            self.push('530 Authentication required')
            return
        self.__state = self.DATA
        self.set_terminator('\r\n.\r\n')
        self.push('354 End data with <CR><LF>.<CR><LF>')
    """


    def found_terminator(self):
        line = smtpd.EMPTYSTRING.join(self.__line)

        if self.debug:
            self.logger.info('found_terminator(): data: %s' % repr(line))

        self.__line = []
        if self.__state == self.COMMAND:
            if not line:
                self.push('500 Error: bad syntax')
                return

            i = line.find(' ')

            if self.authenticating:
                arg = line.strip()
                command = 'AUTH'
            elif i < 0:
                command = line.upper()
                arg = None
            else:
                command = line[:i].upper()
                arg = line[i + 1:].strip()

            # White list of operations that are allowed prior to AUTH.
            # if not command in ['AUTH', 'EHLO', 'HELO', 'NOOP', 'RSET', 'QUIT', 'MAIL']:
            if command in ['DATA']:
                if not self.authenticated and not self.__collect_rcpttos:
                    self.push('530 Authentication required')
                    return

            method = getattr(self, 'smtp_' + command, None)
            if not method:
                self.push('502 Error: command "%s" not implemented' % command)
                return
            method(arg)
            return
        else:
            if self.__state != self.DATA:
                self.push('451 Internal confusion')
                return

            data = []
            for text in line.split('\r\n'):
                if text and text[0] == '.':
                    data.append(text[1:])
                else:
                    data.append(text)
            self.__data = smtpd.NEWLINE.join(data)
            status = self.__server.process_message(
                self.username,
                self.uid,
                self.__mailfrom,
                self.__rcpttos,
                self.__collect_rcpttos,
                self.__data,
                self.__peer[0],
                self.__greeting,
            )
            self.__rcpttos = []
            self.__collect_rcpttos = {}
            self.__mailfrom = None
            self.__state = self.COMMAND
            self.set_terminator('\r\n')
            if not status:
                self.push('250 Ok')
            else:
                self.push(status)


class SMTPServer(asyncore.dispatcher):
    def __init__(self, addr, user_validator=None, ip_validator=None, domain_validator=None, collect_domain_validator=None, timeout=600):
        asyncore.dispatcher.__init__(self)

        self.user_validator = user_validator
        self.ip_validator = ip_validator
        self.domain_validator = domain_validator
        self.collect_domain_validator = collect_domain_validator
        self.timeout = timeout

        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind(addr)
            self.listen(5)
        except socket.error, e:
            self.close()
            raise e

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            channel = SMTPChannel(self, conn, addr, user_validator=self.user_validator, ip_validator=self.ip_validator,
                                  domain_validator=self.domain_validator, collect_domain_validator=self.collect_domain_validator)

            # close connections which accept 10 minutes ago
            channel.accept_time = time.time()
            pid = os.getpid()
            cache_key = "bs_smtp_check_timeout_pid_%s" % pid
            check_time = redis_db.get(cache_key)
            if not check_time:
                t = time.time()
                redis_db.set(cache_key, t)
                check_time = t

            if time.time() > float(check_time) + self.timeout:
                for k, v in dict(self._map).items():
                    if hasattr(v, 'accept_time') and (v.accept_time + self.timeout < time.time()):
                        log.info('connection timeout: client_ip=%s time=%s' % (v.addr, time.time() - v.accept_time))
                        v.close()
                redis_db.set(cache_key, time.time())

    def handle_error(self):
        log.error(traceback.format_exc())
        self.handle_close()

    def process_message(self, username, uid, mailfrom, rcpttos, collect_rcpttos, data, client_ip, helo):
        try:
            # m = email.message_from_string(data)

            # data = received_template.format(ip=client_ip,
            #                                 helo=helo,
            #                                 host=re.sub(r'.*?@', 'smtp.', mailfrom),
            #                                 mail_id=''.join(random.sample(string.ascii_letters, 12)),
            #                                 mailfrom=mailfrom,
            #                                 date=email.utils.formatdate(localtime=True, usegmt=True)) + data

            # mailfrom_in_body = email.utils.parseaddr(m.get('From'))[1].lower()
            # mailfrom = mailfrom.lower()
            #
            # if username and username.lower() != mailfrom or mailfrom != mailfrom_in_body:
            #     log.info('bad mail from: uid=%s, mailfrom=%s, mail_from_in_body=%s, client_ip=%s', uid, mailfrom, mailfrom_in_body, client_ip)
            #     return

            addresses = set(rcpttos)
            format_ok_addresses = addresses
            # format_ok_addresses = filter(check_email_format, addresses)

            if format_ok_addresses:
                self.save_mail(uid, mailfrom, format_ok_addresses, data, client_ip)
            if collect_rcpttos:
                for k, v in collect_rcpttos.iteritems():
                    self.save_mail(k, mailfrom, set(v), data, client_ip, type='collect')

        except BaseException:
            log.error(traceback.format_exc())


    def save_mail(self, uid, mailfrom, rcpttos, data, client_ip, type='relay'):
        mail_id = str(uuid.uuid1())
        filename = '{},{},{},{}'.format(uid, mailfrom, mail_id, client_ip)
        rcpts_path = settings.DATA_RCPTS_PATH if type=='relay' else settings.DATA_COLLECT_RCPTS_PATH
        mails_path = settings.DATA_MAILS_PATH if type=='relay' else settings.DATA_COLLECT_MAILS_PATH
        with open(os.path.join(rcpts_path, filename), 'wb') as f:
            f.write("\n".join(rcpttos))

        with open(os.path.join(mails_path, filename), 'wb') as f:
            f.write(data)
        log.info('received %s mail: pid=%s, uid=%s, mail_from=%s, ok_rcpts=%s, body_len=%s, mail_id=%s, client_ip=%s' % (
            type, os.getpid(), uid, mailfrom, rcpttos, len(data), mail_id, client_ip))


if __name__ == '__main__':
    globals()['_DEBUG'] = Common.check_debug()
    #Common.init_makedir()
    Common.init_pid_file('bs_esmtpd.pid')
    Common.init_cfg_default()
    # Common.init_logger('Esmtpd', len(sys.argv) > 1, _DEBUG, user=Common.cfgDefault.get('global', 'user'))
    Common.signal_init(kill_children)

    # redis_db = get_redis_connection('default')
    redis_db = get_redis()
    auth = Authentication(connection, redis_db)
    listen_ip = Common.cfgDefault.get('esmtpd', 'listen_ip')
    listen_ports = map(lambda x: int(x), Common.cfgDefault.get('esmtpd', 'listen_port').split(','))
    timeout = int(Common.cfgDefault.get('esmtpd', 'timeout'))

    for listen_port in listen_ports:
        SMTPServer((listen_ip, listen_port),
                   ip_validator=auth.auth_by_ip, user_validator=auth.auth_by_password,
                   domain_validator=auth.auth_by_domain, collect_domain_validator=auth.auth_by_collect_domain, timeout=timeout)
        log.info('emstpd bind on: %s:%s' % (listen_ip, listen_port))

    log.info('esmtpd main (pid=%s) started' % os.getpid())

    Common.init_run_user(Common.cfgDefault.get('global', 'user'))

    #delete key value
    [redis_db.delete(_) for _ in redis_db.keys('bs_smtp_check_timeout_pid*')]

    for i in xrange(3):
        if not os.fork():
            Common.signal_init(handle_exit)
            # signal.signal(signal.SIGINT, handle_exit)
            # signal.signal(signal.SIGTERM, handle_exit)
            # signal.signal(signal.SIGCHLD, handle_exit)
            log.info('esmtpd child (pid=%s) started' % os.getpid())
            break

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
