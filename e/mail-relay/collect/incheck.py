# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
from gevent import monkey
import pyclamd

monkey.patch_time()
monkey.patch_socket()
#monkey.patch_subprocess()

import psycopg2.extensions
import psycopg2.extras

psycopg2.extensions.set_wait_callback(psycopg2.extras.wait_select)

import dns.resolver
import dns.exception

dns.resolver.get_default_resolver().cache = dns.resolver.LRUCache()

import sys
import os
import re
import traceback
import gevent
import gevent.pool
import time
import ipaddr
import lib.SPF2IP as SPF2IP
import lib.spf as spf

from lib import common
from lib.resource import Checklist, SenderChecklist, RegexChecklist

common.init_django_enev()
# from redis_cache import get_redis_connection
from lib.django_redis import get_redis
from django.conf import settings as django_settings
from django.db import DatabaseError, InterfaceError, connection
from django.core.exceptions import ObjectDoesNotExist

from lib.common import outinfo, outerror, strip_tags
from lib.report_spam import spamc, dspamc, esets, savscan_attach, dspamc2
from lib.parse_email import ParseEmail
from lib.ctasd import Ctasd
from lib.validators import check_email_format
from apps.collect_mail.models import get_mail_model
from apps.mail.models import KeywordBlacklist, CheckSettings, SubjectKeywordBlacklist, SenderBlacklist, \
    AttachmentBlacklist, SenderWhitelist, AttachmentTypeBlacklist, CustomerSenderBlacklist, CollectRecipientWhitelist, \
    SpfChecklist, CollectRecipientChecklist, SpfIpWhitelist
from apps.core.models import CustomerSetting

# ###########################################################
# 公共数据

# redis_queue_name
#MAIL_INCHECK_QUEUE = 'collect_incheck'
MAIL_INCHECK_ERROR_QUEUE = 'collect_incheck_error'
MAIL_SEND_QUEUE = 'collect_send'

clamav_sock = ''
incheck_pid_file = ''
MAIL_INCHECK_QUEUE = ''
review_help_mode = None


class DefaultSetting:
    c_spam_score_max = 5.0
    night_spam_score_max = 5.0
    subject_max_size = 0
    content_max_size = 0
    sender_max_size = 0
    spam_max_size = 0
    dspam_max_size = 0
    esets_max_size = 0
    ctasd_max_size = 0
    attachment_min_size = 0
    collect_attachment_min_size = 0


# 对象
# redis = get_redis_connection('default')
redis = get_redis()
ctasd = Ctasd(django_settings.CTASD_HOST, django_settings.CTASD_PORT_IN)
setting = DefaultSetting()

# 变量
_DEBUG = False

# CYBER 自动拒绝主题正则表示
# 网关CYBER中的主题是纯英文的自动拒绝
RES_CYBER_REJECT = u'^[ -~]*$'

signal_stop = False
_MAXTHREAD = 50
blacklist = {}

spf_checklist = {}
# 发件人白名单
# 结构{'customer_id':{'is_domain': [], 'not_domain': []}}
sender_checklist = {}
sender_whitelist = {}
recipient_whitelist = []
recipient_checklist = {}
# 小危附件类型黑名单
attach_type_blacklist = []

# SPF IP白名单
spf_ip_whitlist = []

# 直接拒绝的检测结果
check_result_reject = ['auto_reject', 'virus', 'spam', 'error_format', 'auto_reject_cyber', 'auto_reject_attach',
                       'savi', 'c_sender_blacklist']
# 直接通过的检测结果
check_result_pass = ['innocent', 'sender_whitelist']
# 直接垃圾学习的检测结果
check_auto_study = ['auto_reject_cyber']

# ctasd垃圾状态
ctasd_spam_status = ['confirmed', 'bulk', 'suspect']
# ctasd病毒状态
ctasd_virus_status = ['virus', 'high', 'medium']


# ###########################################################
REG = re.compile(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\].*by (tt-los|tt-hz|tt-hz2|tt-los2)\.spamgateway\.cn', re.DOTALL)


def get_real_client_ip(message_object, client_ip):
    if client_ip in ('104.250.149.146', '192.168.50.3', '192.168.50.4', '162.251.94.64'):
        l = message_object.get_all('Received')
        if l:
            for h in reversed(l):
                m = REG.search(h)
                if m:
                    return m.group(1)
    return client_ip

def check_list(domain, list):
    return domain in list
    for l in list:
        if domain.endswith(l):
            return True
    return False


def check_spf1(sender, ip):
    domain = sender.split('@')[-1]
    array = SPF2IP.SPF2IP(domain).IPArray()
    if len(array) == 0:
        return None
    ip = ipaddr.IPv4Address(ip)
    for net in array:
        if ip in ipaddr.IPv4Network(net):
            return True
    return False


def check_spf2(sender, ip):
    r = spf.check2(i=ip, s=sender, h='')
    if r[0] == 'pass':
        return True, r
    elif r[0] in ('fail', 'softfail'):
        return False, r
    else:
        return None, r


def check_spf(sender, ip):
    try:
        r1 = check_spf1(sender, ip)
        if r1 is not False:
            outinfo('check_spf({!r}, {!r}): SPF2IP pass'.format(sender, ip))
            return True
        r2, d = check_spf2(sender, ip)
        if r2 is not False:
            outinfo('check_spf({!r}, {!r}): spf.check2 pass {}'.format(sender, ip, d))
            return True
        else:
            outinfo('check_spf({!r}, {!r}): spf.check2 fail {}'.format(sender, ip, d))
            return False
    except BaseException as e:
        outinfo('check_spf({!r}, {!r}): exception {}'.format(sender, ip, repr(e)))
        return True


# 处理器

class Processor(object):
    def __init__(self, task):

        # 邮件基本信息
        self.task = task
        self.task_date, self.task_id = task.split(',')[:2]
        self.model = get_mail_model(self.task_date)
        self.mail_obj = self.model.objects.get(pk=self.task_id)
        self.uid = self.mail_obj.customer.id


    def _init(self):
        self.key = self.mail_obj.get_mail_filename()
        self.mail_content = self.mail_obj.get_mail_content()
        self.size = self.mail_obj.size
        self.mail_from = self.mail_obj.mail_from.lower()
        self.mail_to = self.mail_obj.mail_to.lower()
        self.mail_path = self.mail_obj.get_mail_path()
        self.subject = self.mail_obj.subject
        self.same_mails = self.model.objects.filter(mail_id=self.task_id, state__in=['check', 'review'])
        self.same_keys = [m.get_mail_filename() for m in self.same_mails]
        self.parse_obj = ParseEmail(self.mail_content)
        self.parse_data = self.parse_obj.parseMailTemplate()
        # self.content = strip_tags(self.parse_obj.get_content(self.parse_data))
        self.content = self.parse_obj.get_content(self.parse_data)
        self.customer_setting, _ = CustomerSetting.objects.get_or_create(customer_id=self.uid)
        self.task_info = self.task.decode('utf-8', 'ignore')
        self.attachments = self.parse_data.get('attachments', [])
        self.client_ip = self.mail_obj.client_ip
        self.real_client_ip = get_real_client_ip(self.parse_obj.obj, self.client_ip)


    # 运行处理器
    @common.fn_timer
    def run(self):
        self._init()
        if not os.path.exists(self.mail_path):
            outerror(u'not found mail file: {}'.format(self.task))
            return


        # 发件人格式检测
        if self._do_check_format():
            return


        # 白名单监测
        if self._do_sender_checklist('sender_whitelist'):
            return

        # 黑名单监测
        if self._do_sender_checklist('c_sender_blacklist'):
            return

        # 小危附件监测
        if self._do_attach_check():
            return

        # 免审关键字过滤
        if self._do_auto_reject():
            return

        # dspam垃圾检测
        if self._dspamc():
            return

        # spf 检测
        if self._check_spf():
            return

        if self._do_virus():
            return

        # ctasd检测
        if self._ctasd_spam():
            return

        # esets 病毒检测
        #if self._esets():
        #    return

        # savi垃圾检测
        # if self._savi():
        # return


        #发件人黑名单检测
        if self._do_sender_blacklist():
            return

        #主题关键字黑名单检测
        if self._do_subject_keyword_blacklist():
            return

        #内容关键字黑名单检测
        if self._do_keyword_blacklist():
            return

        #spam垃圾检测
        if self._spamc():
            return

        #高危邮件检测
        self._do_high_risk()

        #收件人强制检测名单
        self._do_recipient_checklist()

        return

    @common.fn_timer
    def _dspamc(self):
        if not self.customer_setting.check_dspam:
            return False
        if setting.dspam_max_size and self.size > setting.dspam_max_size:
            return False
        try:
            with gevent.Timeout(60):
                #res = dspamc2(self.mail_content)
                res = dspamc(self.mail_path)
                #self.mail_obj.dspam_sig = res.get('signature', '')
                result = res.get('class', '')
                if result in ['virus', 'spam']:
                    message = res.get('message', '')
                    self.mail_obj.check_result = result
                    self.mail_obj.check_message = message
                    outinfo(u'[Dspam] {}: {}'.format(self.task_info, message))
                    return True
        except gevent.Timeout:
            outerror(u'dspam check time out :{}'.format(self.task_info))
            outerror(traceback.format_exc())
        except BaseException as e:
            outerror(u'dspam check error :{}'.format(self.task_info))
            outerror(traceback.format_exc())
        return False

    # 病毒邮件检测
    @common.fn_timer
    def _do_virus(self):
        # 进行病毒邮件检测
        try:
            pyclamd.init_unix_socket(clamav_sock)
            res = pyclamd.scan_file(self.mail_path)
        except Exception, err:
            outerror(u'virus check error :{}'.format(self.task_info))
            outerror(traceback.format_exc())
            return False

        # 邮件没有病毒时，直接返回
        if res:
            try:
                detail = res.values()[0][1]
            except:
                detail = 'virus'

            outinfo(u'[ClamAV] {}: {}'.format(self.task_info, detail))
            self.mail_obj.check_result = 'virus'
            self.mail_obj.check_message = detail
            return True
        return False

    def _esets_old(self):
        res = esets(self.mail_path)
        if res['action'] not in ('accepted', 'exception'):
            self.mail_obj.check_result = 'esets'
            self.mail_obj.check_message = res['message']
            outinfo(u'[Esets] {}'.format(self.task_info))
            return True
        return False

    def _esets(self):
        try:
            if setting.esets_max_size and self.size > setting.esets_max_size:
                return False
            res = self.parse_obj.get_attr('X-EsetResult', '').lower()
            res_anti = self.parse_obj.get_attr('X-ESET-Antispam', '').lower()
            if res_anti == 'spam':
                if res == 'infected':
                    self.mail_obj.check_result = 'esets_av'
                else:
                    self.mail_obj.check_result = 'esets'
                outinfo(u'[Esets] {}'.format(self.task_info))
                return True
        except BaseException as e:
            outerror(u'esets error :{}'.format(self.task_info))
            outerror(traceback.format_exc())
        return False

    def _savi(self):
        for attach in self.attachments:
            res = savscan_attach(attach)
            if res:
                message = ','.join(res)
                self.mail_obj.check_message = message
                self.mail_obj.check_result = 'savi'
                outinfo(u'[Savi] {}: {}'.format(self.task_info, message))
                return True
        return False

    @common.fn_timer
    def _ctasd_spam(self):
        # check size
        if not self.customer_setting.check_ctasd:
            return False
        if setting.ctasd_max_size and self.size > setting.ctasd_max_size:
            return False
        try:
            with gevent.Timeout(60):
                r = ctasd.check_in_mail_data(self.mail_content,
                                             self.client_ip.encode('utf-8'),
                                             self.mail_from.encode('utf-8'))
                res_spam = r['X-CTCH-Spam'].lower()
                res_virus = r['X-CTCH-VOD'].lower()
                if res_spam in ctasd_spam_status:
                    if re.match(RES_CYBER_REJECT, self.subject):
                        self.mail_obj.check_result = 'auto_reject_cyber'
                        outinfo(u'[Ctasd:Spam] {}: {}: auto_reject_cyber'.format(self.task_info, res_spam))
                    else:
                        self.mail_obj.check_result = 'cyber_spam'
                        outinfo(u'[Ctasd:Spam] {}: {}'.format(self.task_info, res_spam))
                    self.mail_obj.check_message = 'X-CTCH-Spam: {}'.format(r['X-CTCH-Spam'])
                    return True
                elif res_virus in ctasd_virus_status:
                    self.mail_obj.check_result = 'cyber_spam'
                    self.mail_obj.check_message = 'X-CTCH-VOD: {}'.format(res_virus)
                    outinfo(u'[Ctasd:Virus] {}: {}'.format(self.task_info, res_virus))
                    return True
        except gevent.Timeout:
            outerror(u'ctasd check time out :{}'.format(self.task_info))
            outerror(traceback.format_exc())
        except BaseException as e:
            outerror(u'ctasd check error :{}'.format(self.task_info))
            outerror(traceback.format_exc())
        return False

    # @common.fn_timer
    @common.fn_timer
    def _spamc(self):
        if not self.customer_setting.check_spam:
            return False
        if setting.spam_max_size and self.size > setting.spam_max_size:
            self.mail_obj.check_result = 'innocent'
            return False
        res = spamc(self.mail_path)
        score = res.get('score', 0)
        self.mail_obj.check_message = res.get('message', '').replace('5.0', str(setting.c_spam_score_max))
        outinfo(u'[Spam] {}: {}'.format(self.task_info, score))

        if float(score) < setting.c_spam_score_max:
            self.mail_obj.check_result = 'innocent'
            return False
        else:
            self.mail_obj.check_result = 'spamassassin'
            return True


    # @common.fn_timer
    def finish(self):
        if not self.mail_obj.check_result:
            self.mail_obj.check_result = 'innocent'
        check_result = self.mail_obj.check_result
        try:
            # 清空邮件
            # 直接拒绝
            if check_result in check_result_reject:
                self.mail_obj.review_result = 'reject'
                self.mail_obj.state = 'reject'
            elif check_result in check_result_pass:
                self.mail_obj.review_result = 'pass'
                self.mail_obj.state = 'send'
            # 需要审核
            else:
                self.mail_obj.state = 'review'
                redis.lpush('collect_sync', self.key)
            self._do_check_for_same_mail()
            if not self._do_check_recipient_whitelist(self.mail_obj):
                self.mail_obj.save(update_fields=['check_result', 'check_message', 'review_result', 'state', 'dspam_sig'])
                if check_result in check_result_pass:
                    self.mail_obj.save_mail_for_pop()
                    redis.lpush(MAIL_SEND_QUEUE, self.key)
                if check_result in check_auto_study:
                    redis.lpush('dspam_collect_reject', self.key)
            if review_help_mode == 'client' and self.mail_obj.state == 'review':
                redis.lpush('control_review_help', 'collect,' + self.task)
        except BaseException as e:
            outerror(u'finish error:{}'.format(self.task_info))
            outerror(traceback.format_exc())

    def _do_check_for_same_mail(self):
        mail_obj = self.mail_obj
        for m in self.same_mails:
            if not self._do_check_recipient_whitelist(m):
                m.check_result = mail_obj.check_result
                m.check_message = mail_obj.check_message
                m.state = mail_obj.state
                m.review_result = mail_obj.review_result
                m.save(update_fields=['check_result', 'check_message', 'review_result', 'state', 'dspam_sig'])
                if mail_obj.check_result in check_result_pass:
                    redis.lpush(MAIL_SEND_QUEUE, m.get_mail_filename())
                outinfo(u'check same mail:{}'.format(m.get_mail_filename()))

    def handle_error(self):
        try:
            self.mail_obj.check_result = 'error'
        except:
            outerror(u'handle error:{}'.format(self.task_info))
            outerror(traceback.format_exc())

    def _do_spf_ip_whitelist(self):
        """
        检测IP是否在SPF IP白名单中，如果在，则跳过SPF
        :return:
        """
        return self.client_ip in spf_ip_whitlist or self.real_client_ip in spf_ip_whitlist

    def _check_spf(self):
        if self._do_check_spf():
            #强制SPF检查域名库 中的免审直接拒绝
            domain = self.mail_from.split('@')[-1].lower()
            for k, v in spf_checklist.iteritems():
                #if domain.endswith(k) and v:
                if domain == k and v:
                    self.mail_obj.check_result = 'auto_reject'
                    self.mail_obj.check_message = 'spf'
                    outinfo(u'[spf]:direct reject: {} {}'.format(self.task_info, self.mail_from))
                    return True
            return True
        return False

    def _do_check_spf(self):
        if self.mail_obj.check_result == 'spf':
            return True
        domain = self.mail_from.split('@')[-1].lower()

        if self.customer_setting.check_spf or check_list(domain, spf_checklist):
            if not self._do_spf_ip_whitelist() and not check_spf(self.mail_from, self.real_client_ip):
                self.mail_obj.check_result = 'spf'
                outinfo(u'[spf]:{}: {} {}'.format(self.task_info, self.mail_from, self.real_client_ip))
                return True
        return False


    def _do_check_format(self):
        if not self.subject and not self.content and not self.attachments:
            self.mail_obj.check_result = 'error_format'
            outinfo(u'[ErrorFormat]:{}: no content'.format(self.task_info))
            return True
        if not self.customer_setting.check_format:
            return False
        if not check_email_format(self.mail_from, is_check_suffix=False):
            self.mail_obj.check_result = 'error_format'
            outinfo(u'[ErrorFormat]:{}: {}'.format(self.task_info, self.mail_from))
            return True
        return False

    def _do_sender_checklist(self, key):
        """
        发件人白名单　黑名单检测
        :param key: sender_whitelist or c_sender_blacklist
        :return:
        """
        try:
            res, msg = sender_checklist[key].search(self.uid, self.mail_from)
            if res:
                # 发件人白名单必须检测spf
                if key == 'sender_whitelist':
                    if not self._do_spf_ip_whitelist() and not check_spf(self.mail_from, self.real_client_ip):
                        self.mail_obj.check_result = 'spf'
                        outinfo(u'[spf]:{}: {} {}'.format(self.task_info, self.mail_from, self.real_client_ip))
                        return False

                outinfo(u'[{}]{}: {}'.format(key, self.task_info, msg))
                self.mail_obj.check_result = key
                self.mail_obj.check_message = msg
                return True
        except BaseException, e:
            outerror(u'{} error:{}'.format(key, self.task_info))
            outerror(traceback.format_exc())
        return False


    def _do_check_keyword(self, check_str, keyword_key, direct_reject=False):
        search_s, s = blacklist[keyword_key].search(check_str, is_dr=direct_reject)
        if search_s:
            outinfo(u'[{}]:{}: {}'.format(keyword_key, self.task_info, search_s))
            self.mail_obj.check_result = keyword_key if keyword_key != 'attach_blacklist' else 'high_risk'
            self.mail_obj.check_message = u'{}----{}'.format(search_s, s)
            self._do_auto_review(keyword_key, direct_reject)
            return True
        return False


    def _do_auto_review(self, step, direct_reject=False):
        # 判断是否直接拒绝
        if direct_reject:
            outinfo(u'{}: {} direct_reject'.format(self.task_info, step))
            self.mail_obj.check_result = 'auto_reject'
            self.mail_obj.check_message += '({})'.format(step)
            return

    # @Common.fn_timer
    def _do_sender_blacklist(self, direct_reject=False):
        if not self.customer_setting.check_sender and not direct_reject:
            return False
        if setting.sender_max_size and self.size > setting.sender_max_size:
            return False
        sender1 = self.mail_from
        sender2 = self.parse_obj.get_attr('from')
        if not sender2:
            sender2 = ''
        return self._do_check_keyword(sender1, 'sender_blacklist', direct_reject) or self._do_check_keyword(sender2, 'sender_blacklist', direct_reject)

    # @common.fn_timer
    def _do_subject_keyword_blacklist(self, direct_reject=False):
        if not self.customer_setting.check_subject and not direct_reject:
            return False
        if setting.subject_max_size and self.size > setting.subject_max_size:
            return False
        if not self.subject:
            return False
        return self._do_check_keyword(self.subject, 'subject_blacklist', direct_reject)

    # @common.fn_timer
    def _do_keyword_blacklist(self, direct_reject=False):
        if not self.customer_setting.check_content and not direct_reject:
            return False
        if setting.content_max_size and self.size > setting.content_max_size:
            return False
        return self._do_check_keyword(self.content, 'keyword_blacklist', direct_reject)


    def _do_high_risk(self):
        if not self.customer_setting.check_high_risk:
            return False
        attachments = self.attachments
        if setting.attachment_min_size and len(attachments) == 1:
            attachment = attachments[0]
            if attachment['decode_name'].split('.')[-1] in ['rar', 'zip', 'jar'] and attachment[
                'size'] <= setting.attachment_min_size:
                self.mail_obj.check_result = 'high_risk'
                self.mail_obj.check_message = attachment['decode_name']
                outinfo(u'[HighRisk(min_attachment)]: {}'.format(self.task_info))
                return True
        if self._do_attach_blacklist():
            return True
        return False

    def _do_attach_blacklist(self, direct_reject=False):
        attachments = self.attachments
        for a in attachments:
            name = a['decode_name']
            if self._do_check_keyword(name, 'attach_blacklist', direct_reject):
                return True
        return False


    def _do_auto_reject(self):
        # 发件人黑名单检测
        if self._do_sender_blacklist(direct_reject=True):
            return True

        # 主题关键字黑名单检测
        if self._do_subject_keyword_blacklist(direct_reject=True):
            return True

        # 附件关键字黑名单检测
        if self._do_attach_blacklist(direct_reject=True):
            return True

        # 内容关键字黑名单检测
        if self._do_keyword_blacklist(direct_reject=True):
            return True
        return False


    def _do_attach_check(self):
        """
        小危附件：自动删除 非中文 邮件中 xxx 附件类型 且 小于XXX KB的邮件，直接删除，不审核，不学习。过滤顺序在 发件人白名单检测 之后。
        :return:
        """
        attachments = self.attachments
        if setting.collect_attachment_min_size and len(attachments) == 1:
            try:
                attachment = attachments[0]
                filename = attachment['decode_name']
                if filename.split('.')[-1] in attach_type_blacklist and attachment[
                    'size'] <= setting.collect_attachment_min_size and re.match(RES_CYBER_REJECT,
                                                                                filename) and (
                            not self.subject or re.match(RES_CYBER_REJECT,
                                                         self.subject)):
                    self.mail_obj.check_result = 'auto_reject_attach'
                    self.mail_obj.check_message = filename
                    outinfo(u'[SmallRiskAttach(min_attachment)]: {}'.format(self.task_info))
                    return True
            except:
                outerror(u'attach_type_blacklist error:{}'.format(self.task_info))
                outerror(traceback.format_exc())
        return False

    #网关收件人白名单处理
    def _do_check_recipient_whitelist(self, mail_obj):
        """
         网关收件人白名单, 如果收件人在白名单中，网关对该发件人不做任何过滤
        :return:
        """
        try:
            if mail_obj.mail_to in recipient_whitelist:
                outinfo(u'[RecipientWhitelist]:{}'.format(mail_obj.get_mail_filename()))
                mail_obj.check_result = 'recipient_whitelist'
                mail_obj.check_message = self.mail_obj.check_message
                mail_obj.review_result = 'pass'
                mail_obj.state = 'send'
                mail_obj.save(update_fields=['check_result', 'check_message', 'review_result', 'state'])
                redis.lpush(MAIL_SEND_QUEUE, mail_obj.get_mail_filename())
                return True
        except BaseException as e:
            outerror('recipient whitelist error:{}'.format(mail_obj.get_mail_filename()))
            outerror(traceback.format_exc())
        return False

    def _do_recipient_checklist(self):
        """
        网关收件人强制检测名单
        :param key:
        :return:
        """
        try:
            res, msg = recipient_checklist.search(self.mail_to)
            if res:
                outinfo(u'[force_check]{}: {}'.format(self.task_info, msg))
                self.mail_obj.check_result = 'force_check'
                self.mail_obj.check_message = msg
                return True
        except BaseException, e:
            outerror(u'force check error:{}'.format(self.task_info))
            outerror(traceback.format_exc())
        return False


# ###########################################################
# 线程

# 任务执行线程
def worker(task):
    try:
        p = Processor(task)
        p.run()
    except ObjectDoesNotExist, e:
        outerror('ObjectDoesNotExist: {}'.format(task))
        outerror(traceback.format_exc())
        # redis.rpush(MAIL_INCHECK_QUEUE, task)
        return
    except (DatabaseError, InterfaceError), e:
        # 如果报数据库异常，关闭连接，重新处理任务
        outerror('DatabaseError: {}'.format(task))
        outerror(traceback.format_exc())
        connection.close()
        # redis.rpush(MAIL_INCHECK_QUEUE, task)
        gevent.sleep(10)
        return
    except:
        outerror(traceback.format_exc())
        outerror(u'processor error:{}'.format(task))
        p.handle_error()
    finally:
        try:
            p.finish()
        except:
            redis.rpush(MAIL_INCHECK_ERROR_QUEUE, task)
    return


# 队列扫描管理线程
def scanner():
    pool = gevent.pool.Pool(_MAXTHREAD)
    while True:
        if signal_stop: break

        # 尝试从从队列中取出任务
        # date,id  (example:2015-05-15,123)
        task = redis.rpop(MAIL_INCHECK_QUEUE)
        if not task:
            gevent.sleep(0.1)
            continue
        pool.spawn(worker, task)
        outinfo(u'pool len: {}'.format(len(pool)))

    pool.join()
    return

# 初始化全局变量
def init_resource():
    global setting, sender_whitelist, attach_type_blacklist, blacklist, sender_checklist, recipient_whitelist, spf_checklist, recipient_checklist, spf_ip_whitlist
    blacklist = {
        'keyword_blacklist': Checklist(KeywordBlacklist),
        'subject_blacklist': Checklist(SubjectKeywordBlacklist),
        'attach_blacklist': Checklist(AttachmentBlacklist),
        'sender_blacklist': Checklist(SenderBlacklist)
    }

    sender_checklist = {
        'sender_whitelist': SenderChecklist(SenderWhitelist),
        'c_sender_blacklist': SenderChecklist(CustomerSenderBlacklist)
    }

    attach_type_blacklist = AttachmentTypeBlacklist.objects.filter(disabled=False).values_list('keyword', flat=True)
    recipient_whitelist = CollectRecipientWhitelist.objects.filter(disabled=False).values_list('keyword', flat=True)
    recipient_checklist = RegexChecklist(CollectRecipientChecklist)
    spf_ip_whitlist = SpfIpWhitelist.objects.filter(disabled=False).values_list('keyword', flat=True)

    spf_checklist = dict(SpfChecklist.objects.filter(disabled=False).values_list('domain', 'direct_reject'))

    settings = CheckSettings.objects.all()

    if settings:
        setting = settings[0]
        setting.subject_max_size *= 1024
        setting.content_max_size *= 1024
        setting.spam_max_size *= 1024
        setting.dspam_max_size *= 1024
        setting.esets_max_size *= 1024
        setting.ctasd_max_size *= 1024
        setting.attachment_min_size *= 1024
        setting.collect_attachment_min_size *= 1024
        setting.sender_max_size *= 1024
        h = int(time.strftime('%H'))
        if h >= 19 or h < 7:
            setting.c_spam_score_max = setting.c_night_spam_score_max


def init_resource_routine():
    while redis.rpoplpush(MAIL_INCHECK_ERROR_QUEUE, MAIL_INCHECK_QUEUE) is not None:
        pass
    while True:
        if signal_stop: break
        try:
            outinfo(u'init resouce routine')
            init_resource()
        except BaseException as e:
            outerror(u'init_resource_routine exception')
        gevent.sleep(180)


# ###########################################################

# 信号量处理
def signal_handle(mode):
    outinfo(u"catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

def init_queue_and_pidfile():
    global MAIL_INCHECK_QUEUE, incheck_pid_file
    if len(sys.argv) > 1:
       MAIL_INCHECK_QUEUE = sys.argv[1]
       incheck_pid_file = MAIL_INCHECK_QUEUE + '.pid'


if __name__ == "__main__":
    globals()['_DEBUG'] = common.check_debug()
    init_queue_and_pidfile()
    common.init_cfg_default()
    common.init_run_user(common.cfgDefault.get('global', 'user'))
    common.init_makedir()
    common.init_pid_file(incheck_pid_file)
    common.init_logger(MAIL_INCHECK_QUEUE, len(sys.argv) > 2, _DEBUG)
    clamav_sock = common.cfgDefault.get('clamav', 'sock')
    review_help_mode = common.cfgDefault.get('review_help', 'mode')
    init_resource()
    gevent.spawn(init_resource_routine)

    # 运行程序
    EXIT_CODE = 0
    outinfo(u"program start")
    try:
        # 设置监听信号量
        common.gevent_signal_init(signal_handle)
        scanner()
    except KeyboardInterrupt:
        signal_handle('sigint')
    except:
        outerror(traceback.format_exc())
        EXIT_CODE = 1
    outinfo(u"program quit")
    sys.exit(EXIT_CODE)
