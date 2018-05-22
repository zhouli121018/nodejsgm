#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import datetime
import email.encoders
import email.mime.base
import email.mime.multipart
import email.mime.text
import gevent.pool
import json
import logging
import re
import smtplib

import lib.del_attach_from_msg
import lib.common

lib.common.init_django_enev()

from django.db.transaction import atomic
from django.db import InterfaceError, DatabaseError, connection
from django.core.exceptions import ObjectDoesNotExist
from deliver.lib.utility import decode_msg
from apps.core.models import CustomerSetting
from apps.mail.models import BounceSettings
from apps.collect_mail.models import get_mail_model

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('collect')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)

redis = lib.common.get_redis_cli()


def safe_format(template, **kwargs):
    def replace(mo):
        name = mo.group('name')
        if name in kwargs:
            return unicode(kwargs[name])
        else:
            return mo.group()

    p = r'\{(?P<name>[A-Za-z]+)\}'
    return re.sub(p, replace, template)


def bounce_message(sender, receiver, html_text, origin_message):
    m = email.mime.multipart.MIMEMultipart('report', report_type='delivery-status')
    m['From'] = sender
    m['To'] = receiver
    m['Subject'] = 'Bounce Message'

    p1 = email.mime.text.MIMEText(html_text, 'html', 'utf-8')
    m.attach(p1)

    p2 = email.mime.base.MIMEBase('message', 'rfc822')
    p2.set_payload(origin_message)
    p2.add_header('Content-Disposition', 'attachment', filename='origin.eml')
    email.encoders.encode_base64(p2)
    m.attach(p2)

    return m.as_string()


def send(host, port, sender, password, receiver, message):
    try:
        s = smtplib.SMTP(host, port)

        code, msg = s.login(sender, password)
        if not (200 <= code <= 299):
            return code, msg

        s.sendmail(sender, receiver, message)
        s.quit()
        return 250, 'ok'
    except smtplib.SMTPResponseException as e:
        code, msg = e.smtp_code, e.smtp_error
        return code, msg
    except smtplib.SMTPRecipientsRefused as e:
        senderrs = e.recipients
        code, msg = senderrs[receiver]
        return code, msg
    except BaseException as e:
        log.warning(u'send: exception', exc_info=1)
        code, msg = -1, repr(e)
        return code, msg


def bounce(j):
    d = json.loads(j)
    date, id = d['mail_ident'].split(',')[:2]

    while True:
        try:
            mail = get_mail_model(date).objects.get(id=id)

            try:
                enable = CustomerSetting.objects.filter(customer=mail.customer, c_bounce=True).first()
            except ObjectDoesNotExist:
                enable = False

            if enable:
                bounce_setting = BounceSettings.objects.get()

                sender = bounce_setting.mailbox
                receiver = d['sender']

                html_text = safe_format(bounce_setting.template_cn,
                                        receiver=d['receiver'],
                                        subject=mail.subject,
                                        date=d.get('deliver_time'),
                                        reason=mail.return_message_display())

                # origin_message = mail.get_mail_content()
                try:
                    origin_message = lib.del_attach_from_msg.del_attach_from_msg(d['mail_ident'], f='collect')
                except IOError:
                    origin_message = ''

                message = bounce_message(sender, receiver, html_text, origin_message)

            break
        except BaseException as e:
            log.warning(u'bounce: exception', exc_info=1)
            gevent.sleep(60)

    if enable:
        code, msg = send(bounce_setting.server, bounce_setting.port, sender, bounce_setting.password, receiver, message)
        msg = decode_msg(msg)
        d['bounce_time'] = datetime.datetime.now()
        d['bounce_result'] = code == 250
        d['bounce_message'] = msg
        log.info(
            u'bounce: bounced message, mail_ident={}, code={}, msg={}, reason={}'.format(d['mail_ident'], code, msg,
                                                                                         mail.return_message_display()))
    else:
        log.info(u'bounce: skip bounced message, mail_ident={}'.format(d['mail_ident']))

    (redis.pipeline()
     .lpush('collect_bounced', json.dumps(d, cls=lib.common.ComplexEncoder))
     .lrem('collect_bounce_waiting', 0, j)
     .execute())


def put_routine():
    pool = gevent.pool.Pool(5)
    while True:
        j = redis.brpoplpush('collect_bounce', 'collect_bounce_waiting')
        pool.spawn(bounce, j)


def save(d):
    date, id = d['mail_ident'].split(',')[:2]

    while True:
        try:
            with atomic():
                mail = get_mail_model(date).objects.get(id=id)
                if 'bounce_result' in d:
                    mail.bounce_time = d['bounce_time']
                    mail.bounce_result = 'success' if d['bounce_result'] else 'fail'
                    mail.bounce_message = d['bounce_message']
                if mail.state == 'bounce':
                    mail.state = 'fail_finished' if mail.return_code else 'reject'
                else:
                    log.error(u'save: unexpected state, mail_ident={}, state={}'
                              .format(d['mail_ident'], mail.state))
                mail.save(update_fields=['bounce_time', 'bounce_result', 'bounce_message', 'state'])
            return
        except (DatabaseError, InterfaceError) as e:
            # 如果报数据库异常，关闭连接，重新处理任务
            log.warning(u'DatabaseError: exception', exc_info=1)
            connection.close()
        except BaseException as e:
            log.warning(u'save: exception', exc_info=1)
        gevent.sleep(10)


def sync_db():
    while True:
        j = redis.brpoplpush('collect_bounced', 'collect_bounced_temp')
        d = json.loads(j)
        save(d)
        redis.lrem('collect_bounced_temp', 0, j)
        log.info(u'sync_db: saved to postgres, mail_ident={}'.format(d['mail_ident']))


def init():
    while redis.rpoplpush('collect_bounce_waiting', 'collect_bounce') is not None:
        pass
    while redis.rpoplpush('collect_bounced_temp', 'collect_bounced') is not None:
        pass


def main():
    init()
    gevent.joinall([
        gevent.spawn(put_routine),
        gevent.spawn(sync_db)
    ])


if __name__ == '__main__':
    main()
