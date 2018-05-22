# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#
from gevent import monkey
monkey.patch_time()
monkey.patch_socket()

import sys
import os
import re
import traceback
import gevent
import gevent.pool
import time
import pyclamd

import lib.common         as Common
Common.init_django_enev()
# from redis_cache import get_redis_connection
from lib.django_redis import get_redis

from django.conf import settings as django_settings
from django.db import InterfaceError, DatabaseError, connection
from django.db.models import F
from lib.common import outinfo, outerror, strip_tags
from lib.report_spam import spamc, dspamc
from lib.validators import check_email_format
from lib.parse_email import ParseEmail
from lib.ctasd import Ctasd
from lib.resource import Checklist
from apps.mail.models import get_mail_model, DomainBlacklist, KeywordBlacklist, CheckSettings, SubjectKeywordBlacklist, \
    SubjectKeywordWhitelist, SenderBlacklist, CustomKeywordBlacklist, AttachmentBlacklist, RecipientWhitelist, \
    AttachmentTypeBlacklist, RelaySenderWhitelist, SenderCredit, CreditIntervalSettings
from apps.core.models import CustomerSetting

# ###########################################################
# 公共数据

# redis_queue_name
MAIL_POSTMAN_QUEUE = 'relay_postman'
MAIL_SPAM_QUEUE = 'relay_spam'
MAIL_SUBJECT_HASH = 'relay_incheck_subject'
MAIL_BULK_HASH = 'relay_incheck_bulk'
MAIL_BULK_EXPIRE_HASH = 'relay_incheck_bulk_expire'
MAIL_SENDER_HISTORY = 'relay_sender_history'
SPAM_SENDER = 'relay_spam_sender'
SPAM_SENDER_HISTORY = 'relay_spam_sender_history'
REVIEW_HISTORY = 'relay_review_history'
RELAY_SENDER_GREY_LIST = 'relay_sender_grey_list'
RELAY_SENDER_GREY_LIST_1 = 'relay_sender_grey_list_1'

# 群发数量
bulk_count = 0
bulk_count_key = '_cache_bulk_count'

clamav_sock = ''
incheck_pid_file = ''
MAIL_INCHECK_QUEUE = ''
review_help_mode = None


class DefaultSetting:
    bulk_max = 10
    bulk_expire = 7
    max_size = 50 * 1000000
    spam_score_max = 5.0
    night_spam_score_max = 5.0
    sender_max_size = 0
    subject_max_size = 0
    custom_max_size = 0
    content_max_size = 0
    spam_max_size = 0
    dspam_max_size = 0
    ctasd_max_size = 0
    attachment_min_size = 0
    active_spam_monitor_time = 60
    active_spam_max = 1
    active_spam_check_time = 24
    bulk_sender_max = 10
    bulk_sender_time = 10
    auto_review_time = 3
    auto_review_num = 10
    auto_review_expire = 365
    auto_review_time_start = 7
    auto_review_time_end = 19
    collect_attachment_min_size = 0
    credit = 1000


# 对象
# redis = get_redis_connection('default')
redis = get_redis()
ctasd = Ctasd(django_settings.CTASD_HOST, django_settings.CTASD_PORT_IN)

# 变量

# CYBER 自动拒绝主题正则表示
# 网关CYBER中的主题是纯英文的自动拒绝
RES_CYBER_REJECT = u'^[ -~]*$'

_DEBUG = False
signal_stop = False
_MAXTHREAD = 50
blacklist = {}
# 收件人域名黑名单
domain_blacklist = []
# 收件人白名单
recipient_whitelist = []
recipient_whitelist_domain = []
# 小危附件类型黑名单
attach_type_blacklist = []
# 发件人白名单
sender_whitelist = []
# 中继发件人信誉度键值对
sender_credit_vals = {}
# 发件人信誉度区间，不同的群发频率检测
credit_interval_settings = []


# 直接拒绝的检测结果
check_result_reject = ['domain_blacklist', 'bulk_email', 'big_email', 'error_format', 'auto_reject', 'custom_blacklist',
                       'virus', 'spam', 'auto_reject_attach', 'bulk_email_subject']
# 直接通过的检测结果
check_result_pass = ['innocent', 'auto_pass', 'sender_whitelist']
# 直接清空邮件内容的监测结果
#check_result_clear_mail = ['domain_blacklist', 'bulk_email', 'bulk_email_subject']
check_result_clear_mail = []

# ctasd垃圾状态
ctasd_spam_status = ['confirmed', 'bulk', 'suspect']
#ctasd病毒状态
ctasd_virus_status = ['virus', 'high', 'medium']

setting = DefaultSetting()


# ###########################################################
# 处理器

# 中继收件人白名单检测时，要求 发件人信誉度 高于xxx分，若发件人信任记录里面没有发件人记录则不检测
def is_credit_gt_default(mail_from):
    mail_from = mail_from.lower()
    if mail_from in sender_credit_vals:
        if sender_credit_vals[mail_from] >= setting.credit:
            return True
        return False
    return True
    # credit_obj = SenderCredit.objects.filter(sender=mail_from)
    # if not credit_obj:
    #     return True
    # if credit_obj.filter(credit__gte=setting.credit):
    #     return True
    # return False

def get_bulk_setting_via_sender(mail_from):
    if mail_from in sender_credit_vals:
        credit = sender_credit_vals[mail_from]
    else:
        credit = 1000
    for each in credit_interval_settings:
        if credit >= each['credit_b'] and (credit < each['credit_e'] or not each['credit_e']):
            return each['bulk_max'], each['bulk_sender_time_f'], each['bulk_sender_max']
    return setting.bulk_max, setting.bulk_sender_time, setting.bulk_sender_max

class Processor(object):
    def __init__(self, task):

        # 邮件基本信息
        self.task = task
        self.task_date, self.task_id = task.split(',')[:2]
        model = get_mail_model(self.task_date)
        self.mail_obj = model.objects.get(pk=self.task_id)
        self.uid = self.mail_obj.customer.id
        self.size = self.mail_obj.size
        self.mail_from = self.mail_obj.mail_from.lower()
        self.mail_to = self.mail_obj.mail_to.lower()
        self.mail_path = self.mail_obj.get_mail_path()
        self.subject = self.mail_obj.subject
        self.same_mails = model.objects.filter(mail_id=self.task_id, state__in=['check', 'review'])
        self.mails_count = self.same_mails.count()
        self.same_keys = [m.get_mail_filename() for m in self.same_mails]
        self.key = self.mail_obj.get_mail_filename()
        self.parse_obj = ParseEmail(self.mail_obj.get_mail_content())
        self.parse_data = self.parse_obj.parseMailTemplate()
        # self.content = strip_tags(self.parse_obj.get_content(self.parse_data))
        self.content = self.parse_obj.get_content(self.parse_data)
        self.mail_to_length = model.objects.filter(mail_id=self.task_id).count() + 1
        self.check_result = ''
        self.attachments = self.parse_data.get('attachments', [])
        self.customer_setting, _ = CustomerSetting.objects.get_or_create(customer_id=self.uid)


    # 运行处理器
    # @Common.fn_timer
    def run(self):
        if not os.path.exists(self.mail_path):
            outerror('not found mail file: {}'.format(self.task))
            return
        # 收件人格式检测
        # 无效地址检测
        # 收件人黑名单检测

        # 发件人格式检测
        if self._do_check_format():
            return

        # 发件人白名单检测
        if self._do_check_sender_whitelist():
            return

        #小危附件监测
        if self._do_attach_check():
            return


        # 发件人域名黑名单检测
        if self._do_domain_blacklist():
            return

        # 邮件大小检测
        if self._do_check_mail_size():
            return

        # 群发邮件检测
        if self._do_bulk_email():
            return

        # 免审关键字过滤
        if self._do_auto_reject():
            return

        # dspam垃圾检测
        if self._dspamc():
            return

        # dspam垃圾检测
        if self._do_virus():
            return

        # 发件人黑名单检测
        if self._do_sender_blacklist():
            return

        # 自动回复黑名单检测
        if self._do_custom_keyword_blacklist():
            return

        # 高危发件人检测
        if self._do_high_sender():
            return

        # 主题关键字黑名单检测
        if self._do_subject_keyword_blacklist():
            return

        # 内容关键字黑名单检测
        if self._do_keyword_blacklist():
            return

        # spam垃圾检测
        if self._spamc():
            return

        # 动态SPAM检测
        if self._do_active_spam():
            return

        # 高危邮件检测
        if self._do_high_risk():
            return

        if self._ctasd_spam():
           return

        return

    # @Common.fn_timer
    def _dspamc(self):
        if setting.dspam_max_size and self.size > setting.dspam_max_size:
            return False
        res = dspamc(self.mail_path)
        #self.mail_obj.dspam_sig = res.get('signature', '')
        result = res.get('class', '')
        if result in ['virus', 'spam']:
            message = res.get('message', '')
            self.mail_obj.check_result = result
            self.mail_obj.check_message = message
            outinfo('[Dspam] {}: {}'.format(self.task, message))
            return True
        return False

    # 病毒邮件检测
    def _do_virus(self):
        # 进行病毒邮件检测
        try:
            pyclamd.init_unix_socket(clamav_sock)
            res = pyclamd.scan_file(self.mail_path)
        except Exception, err:
            outerror(u'virus check error :{}'.format(self.task))
            outerror(traceback.format_exc())
            return False

        # 邮件没有病毒时，直接返回
        if res:
            try:
                detail = res.values()[0][1]
            except:
                detail = 'virus'
            outinfo(u'[ClamAV] {}: {}'.format(self.task, detail))
            self.mail_obj.check_result = 'virus'
            self.mail_obj.check_message = detail
            return True
        return False


    def _ctasd_spam(self):
        if setting.ctasd_max_size and self.size > setting.ctasd_max_size:
            return False
        try:
            with gevent.Timeout(60):
                r = ctasd.check_out_mail_data(self.mail_obj.get_mail_content(),
                                              self.mail_from.encode('utf-8'),
                                              self.mail_to_length)
                res_spam = r['X-CTCH-Spam'].lower()
                res_virus = r['X-CTCH-VOD'].lower()
                if res_spam in ctasd_spam_status:
                    self.mail_obj.check_result = 'cyber_spam'
                    self.mail_obj.check_message = 'X-CTCH-Spam: {}'.format(r['X-CTCH-Spam'])
                    outinfo(u'[Ctasd:Spam] {}: {}'.format(self.task, res_spam))
                    return True
                elif res_virus in ctasd_virus_status:
                    self.mail_obj.check_result = 'cyber_spam'
                    self.mail_obj.check_message = 'X-CTCH-VOD: {}'.format(res_virus)
                    outinfo(u'[Ctasd:Virus] {}: {}'.format(self.task, res_virus))
                    return True
        except gevent.Timeout:
            outerror('ctasd check time out :{}'.format(self.task))
            outerror(traceback.format_exc())
        except BaseException as e:
            outerror('ctasd check error :{}'.format(self.task))
            outerror(traceback.format_exc())
        return False

    # @Common.fn_timer
    def _spamc(self):
        if setting.spam_max_size and self.size > setting.spam_max_size:
            self.mail_obj.check_result = 'innocent'
            return False
        res = spamc(self.mail_path)
        score = res.get('score', 0)
        self.mail_obj.check_message = res.get('message', '').replace('5.0', str(setting.spam_score_max))
        outinfo(u'[Spam] {}: {}'.format(self.task, score))

        if float(score) < setting.spam_score_max:
            self.mail_obj.check_result = 'innocent'
            return False
        else:
            self.mail_obj.check_result = 'spamassassin'
            return True

    # @Common.fn_timer
    def finish(self):
        check_result = self.mail_obj.check_result
        self.check_result = check_result
        try:
            # 直接拒绝
            if check_result in check_result_reject:
                self.mail_obj.review_result = 'reject'
                self.mail_obj.state = 'reject'
            # 直接通过
            elif check_result in check_result_pass:
                self.mail_obj.review_result = 'pass'
                self.mail_obj.state = 'dispatch'
            # 需要审核
            else:
                self.mail_obj.state = 'review'
                redis.lpush('relay_sync', self.key)
            #发件人信誉度处理
            if check_result in ['k_auto_reject', 'spam']:
                reason = 'check_dspam' if check_result == 'spam' else 'check_auto_reject'
                redis.lpush('sender_credit', '{}----{}'.format(self.mail_obj.date_id(), reason))
            self._do_check_for_same_mail()

            if not self._do_check_recipient_whitelist(self.mail_obj):
                # 清空邮件
                if check_result in check_result_clear_mail:
                    #群发样本邮件不清除
                    if not (check_result in ['bulk_email', 'bulk_email_subject'] and self._save_bulk_email()):
                        self.mail_obj.clear_mail()
                self.mail_obj.save(
                    update_fields=['check_result', 'check_message', 'review_result', 'state', 'dspam_sig',
                                   'bulk_sample'])
                if check_result in check_result_pass:
                    self.mail_obj.save_mail_for_pop()
                    redis.lpush('relay_dispatch', self.key)
            if review_help_mode == 'client' and self.mail_obj.state == 'review':
                redis.lpush('control_review_help', 'relay,' + self.task)
        except BaseException as e:
            outerror('finish error:{}'.format(self.task))
            outerror(traceback.format_exc())


    def _save_bulk_email(self):
        """
        “中继群发采样”，群发的邮件每50封抓取一封存档，放入技术支持栏目下
        :return:
        """
        global bulk_count
        bulk_count += 1
        if bulk_count % 50 == 0:
            self.mail_obj.bulk_sample = True
            return True
        return False

    def _do_check_for_same_mail(self):
        mail_obj = self.mail_obj
        for m in self.same_mails:
            if not self._do_check_recipient_whitelist(m):
                if self.check_result in check_result_clear_mail:
                    m.clear_mail()
                m.check_result = self.check_result
                m.check_message = mail_obj.check_message
                m.state = mail_obj.state
                m.review_result = mail_obj.review_result
                m.save(update_fields=['check_result', 'check_message', 'review_result', 'state', 'dspam_sig'])
                if self.check_result in check_result_pass:
                    redis.lpush('relay_dispatch', m.get_mail_filename())
                    # map(lambda key: redis.lpush('relay_dispatch', key), self.same_keys)
                outinfo(u'check same mail:{}'.format(m.get_mail_filename()))


    #中继收件人白名单处理
    def _do_check_recipient_whitelist(self, mail_obj):
        """
        中继收件人域名白名单，凡是收件人域名在白名单中，只做格式检测和DSPAM过滤，然后就直接发送。
        :return:
        """
        # 有多个收件人的不进行处理
        # if self.mails_count:
        #     return False
        # 发件人在发件人白名单中不进行处理
        if self.mail_obj.check_result == 'sender_whitelist':
            return False
        try:
            if (mail_obj.mail_to.lower() in recipient_whitelist or mail_obj.mail_to.split('@')[-1].lower() in recipient_whitelist_domain) \
                    and self.check_result not in ['spam', 'innocent', 'error_format'] and is_credit_gt_default(mail_obj.mail_from):
            #if mail_obj.mail_to.split('@')[-1] in recipient_whitelist and self.check_result not in ['spam', 'innocent',
            #                                                                                        'error_format']:
                outinfo(u'[RecipientWhitelist]:{}'.format(mail_obj.get_mail_filename()))
                # mail_obj.check_result = self.check_result
                mail_obj.check_result = 'recipient_whitelist'
                mail_obj.check_message = self.mail_obj.check_message
                mail_obj.review_result = 'pass'
                mail_obj.state = 'dispatch'
                mail_obj.save(update_fields=['check_result', 'check_message', 'review_result', 'state', 'dspam_sig'])
                mail_obj.save_mail_for_pop()
                redis.lpush('relay_dispatch', mail_obj.get_mail_filename())
                return True
        except BaseException as e:
            outerror('recipient whitelist error:{}'.format(mail_obj.get_mail_filename()))
            outerror(traceback.format_exc())
        return False


    def handle_error(self):
        try:
            self.mail_obj.check_result = 'error'
        except:
            outerror('handle error:{}'.format(self.task))
            outerror(traceback.format_exc())

    def _do_check_format(self):
        if self.mail_from != '<>' and not check_email_format(self.mail_from, is_check_suffix=False):
            self.mail_obj.check_result = 'error_format'
            outinfo(u'[ErrorFormat]:{}: {}'.format(self.task, self.mail_from))
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
                    outinfo(u'[SmallRiskAttach(min_attachment)]: {}'.format(self.task))
                    return True
            except:
                outerror(u'attach_type_blacklist error:{}'.format(self.task))
                outerror(traceback.format_exc())
        return False


    # @Common.fn_timer
    def _do_domain_blacklist(self):
        domain = self.mail_from.split('@')[-1]
        for d in domain_blacklist:
            try:
                r = re.search(d, domain, flags=re.IGNORECASE | re.UNICODE)
                if r:
                    outinfo(u'[DomainBlacklist]:{}: {}'.format(self.task, domain))
                    self.mail_obj.check_result = 'domain_blacklist'
                    self.mail_obj.check_message = u'{}----{}'.format(d, r.group(0))
                    return True
            except:
                outerror('domain_blacklist error:{}'.format(d))
                outerror(traceback.format_exc())
                continue
        return False

    # @Common.fn_timer
    def _do_sender_blacklist(self, direct_reject=False):
        if setting.sender_max_size and self.size > setting.sender_max_size:
            return False
        sender1 = self.mail_from
        sender2 = self.parse_obj.get_attr('from')
        return self._do_check_keyword(sender1 + u'\n' + sender2, 'sender_blacklist', direct_reject)

    # @Common.fn_timer
    def _do_check_mail_size(self):
        if self.size > setting.max_size:
            self.mail_obj.check_result = 'big_email'
            return True
        return False

    # @Common.fn_timer
    def _do_check_sender_whitelist(self):
        sender = self.mail_from
        if sender in sender_whitelist:
            self.mail_obj.check_result = 'sender_whitelist'
            self.mail_obj.check_message = u'发件人白名单'
            outinfo(u'[SenderWhitelist] {}'.format(self.task))
            return True
        return False


    def _do_high_sender(self):

        if redis.hexists(RELAY_SENDER_GREY_LIST, self.mail_from):
            self.mail_obj.check_result = 'high_sender'
            outinfo(u'[HighSender] {}'.format(self.task))
            return True
        return False


    # @Common.fn_timer
    def _do_subject_keyword_blacklist(self, direct_reject=False):
        if setting.subject_max_size and self.size > setting.subject_max_size:
            return False
        if not self.subject:
            return False
        return self._do_check_keyword(self.subject, 'subject_blacklist', direct_reject)

    # @Common.fn_timer
    def _do_keyword_blacklist(self, direct_reject=False):
        if setting.content_max_size and self.size > setting.content_max_size:
            return False
        return self._do_check_keyword(self.content, 'keyword_blacklist', direct_reject)


    def _do_bulk_email(self):
        lua = redis.register_script('''
            local sender, save_time, now = ARGV[1], tonumber(ARGV[2]), tonumber(ARGV[3])
            local a, b

            a = redis.call('hget', KEYS[1], sender)
            b = {}
            if a then
                for t in string.gmatch(a, '[.0-9]+') do
                    if tonumber(t) >= now - save_time then
                        table.insert(b, t)
                    end
                end
            end
            table.insert(b, now)
            redis.call('hset', KEYS[1], sender, table.concat(b, ','))
            return #b
        ''')
        bulk_max, bulk_sender_time, bulk_sender_max = get_bulk_setting_via_sender(self.mail_from)
        n = lua(keys=[MAIL_SENDER_HISTORY],
                args=[self.mail_from, bulk_sender_time, time.time()])
        if n > bulk_sender_max:
            self.mail_obj.check_result = 'bulk_email'
            outinfo(u'[BulkEmails Sender] {}'.format(self.task))
            return True

        # 如果邮件主题在白名单中,不进行群封检测
        if self._check_in_whitelist():
            return False

        subject = u'{}, {}'.format(self.uid, self.subject)
        returnv = False
        if redis.hexists(MAIL_BULK_HASH, subject):
            redis.hincrby(MAIL_BULK_HASH, subject, 1)
            returnv = True
        else:
            inc = redis.hincrby(MAIL_SUBJECT_HASH, subject, 1)

            if inc > bulk_max:
                redis.hset(MAIL_BULK_HASH, subject, inc)
                redis.hset(MAIL_BULK_EXPIRE_HASH, subject, time.time())
                returnv = True
        if returnv:
            self.mail_obj.check_result = 'bulk_email_subject'
            outinfo(u'[BulkEmails] {}'.format(self.task))
        return returnv

    def _check_in_whitelist(self):
        """
        检查邮件主题是否在白名单中
        :return:
        """
        if not self.subject:
            return False
        return self._do_check_keyword(self.subject, 'subject_whitelist')


    def _do_active_spam(self):
        if redis.hexists(SPAM_SENDER, self.mail_from):
            self.mail_obj.check_result = 'active_spam'
            if not self.mail_obj.check_message:
                self.mail_obj.check_message = ''
            outinfo(u'[ActiveSpam] {}: {}'.format(self.task, self.mail_from))
            self._do_auto_review('active_spam')
            return True
        return False

    def _check_same_mailfrom(self):
        try:
            mailfrom_in_mail = self.parse_obj.get_simple_attr('from').lower()
            return self.mail_from.endswith(mailfrom_in_mail)
        except:
            return False

    def _do_high_risk(self):
        attachments = self.attachments
        if setting.attachment_min_size and len(attachments) == 1:
            attachment = attachments[0]
            if attachment['decode_name'].split('.')[-1] in ['rar', 'zip', 'jar'] and attachment[
                'size'] <= setting.attachment_min_size:
                self.mail_obj.check_result = 'high_risk'
                self.mail_obj.check_message = attachment['decode_name']
                outinfo(u'[HighRisk(min_attachment)]: {}'.format(self.task))
                self._do_auto_review('high_risk')
                return True
        if self._do_attach_blacklist():
            return True
        if not self._check_same_mailfrom():
            self.mail_obj.check_result = 'high_risk'
            # self.mail_obj.check_message = u'{}----{}'.format(self.mail_from, mailfrom_in_mail)
            self.mail_obj.check_message = u'发件人不符'
            outinfo(u'[HighRisk(mail_from)]: {}'.format(self.task))
            self._do_auto_review('high_risk')
            return True
        if self.mail_from == '<>':
            self.mail_obj.check_result = 'high_risk'
            self.mail_obj.check_message = u'发件人为空'
            outinfo(u'[HighRisk(not mail_from)]: {}'.format(self.task))
            self._do_auto_review('high_risk')
            return True
        if redis.hexists(RELAY_SENDER_GREY_LIST_1, self.mail_from):
            self.mail_obj.check_result = 'high_risk'
            self.mail_obj.check_message = u'不同发件人名称'
            outinfo(u'[HighRisk(diff sender name)]: {}'.format(self.task))
            self._do_auto_review('high_risk')
            return True
        return False

    def _do_attach_blacklist(self, direct_reject=False):
        attachments = self.attachments
        for a in attachments:
            name = a['decode_name']
            if self._do_check_keyword(name, 'attach_blacklist', direct_reject):
                return True


    # @Common.fn_timer
    def _do_custom_keyword_blacklist(self):
        if not self.customer_setting.check_autoreply:
            return False
        if setting.custom_max_size and self.size > setting.custom_max_size:
            return False
        if self.subject:
            if self._do_check_keyword(self.subject, 'custom_blacklist'):
                return True
        return self._do_check_keyword(self.content, 'custom_blacklist')

    def _do_auto_reject(self):
        #发件人黑名单检测
        if self._do_sender_blacklist(direct_reject=True):
            return True

        #主题关键字黑名单检测
        if self._do_subject_keyword_blacklist(direct_reject=True):
            return True

        #附件关键字黑名单检测
        if self._do_attach_blacklist(direct_reject=True):
            return True

        #内容关键字黑名单检测
        if self._do_keyword_blacklist(direct_reject=True):
            return True
        return False


    def _do_auto_review(self, step, direct_reject=False):
        # 判断是否直接拒绝
        if direct_reject:
            outinfo(u'{}: {} direct_reject'.format(self.task, step))
            self.mail_obj.check_result = 'k_auto_reject'
            self.mail_obj.check_message += '({})'.format(step)
            return

        # 多个收件人不考虑
        if self.same_keys:
            return
        h = int(time.strftime('%H'))
        if setting.auto_review_time_start <= h < setting.auto_review_time_end:
            result = self.auto_review(step)
            if result == 'pass' and is_credit_gt_default(self.mail_from):
                outinfo(u'{}: {} auto_pass'.format(self.task, step))
                self.mail_obj.check_result = 'auto_pass'
                self.mail_obj.check_message += '({})'.format(step)
            elif result == 'reject':
                outinfo(u'{}: {} auto_reject'.format(self.task, step))
                self.mail_obj.check_result = 'auto_reject'
                self.mail_obj.check_message += '({})'.format(step)
            else:
                pass


    def _do_check_keyword(self, check_str, keyword_key, direct_reject=False):
        search_s, s = blacklist[keyword_key].search(check_str, is_dr=direct_reject)
        if search_s:
            outinfo(u'[{}]:{}: {}'.format(keyword_key, self.task, search_s))
            self.mail_obj.check_result = keyword_key if keyword_key != 'attach_blacklist' else 'high_risk'
            self.mail_obj.check_message = u'{}----{}'.format(search_s, s)
            if keyword_key in ['keyword_blacklist', 'subject_blacklist', 'attach_blacklist',
                               'sender_blacklist'] and direct_reject:
                outinfo(u'{}: {} direct_reject'.format(self.task, keyword_key))
                self.mail_obj.check_result = 'k_auto_reject'
                self.mail_obj.check_message += '({})'.format(keyword_key)
            return True
        return False


    def auto_review(self, step):
        """
        :param sender:
        :param receiver:
        :return: 'pass', 'reject' or 'manual'
        """

        lua = redis.register_script('''
            local sender_receiver, save_time, expire_time, number, now =
                ARGV[1],
                tonumber(ARGV[2]),
                tonumber(ARGV[3]),
                tonumber(ARGV[4]),
                tonumber(ARGV[5])

            local a, b, h, h1, r

            a = redis.call('hget', KEYS[1], sender_receiver)
            r = 'manual'
            if a then
                b = cjson.decode(a)
                h = b.history
                if now >= h[#h] + expire_time then
                    redis.call('hdel', KEYS[1], sender_receiver)
                else
                    h1 = {}
                    for _, t in ipairs(h) do
                        if tonumber(t) >= h[#h] - save_time then
                            table.insert(h1, t)
                        end
                    end
                    b.history = h1
                    redis.call('hset', KEYS[1], sender_receiver, cjson.encode(b))
                    if #h1 >= number then
                        r = b.result
                    end
                end
            end
            return r
        ''')

        key = '{}:{}'.format(REVIEW_HISTORY, step)

        return lua(keys=[key],
                   args=['{},{}'.format(self.mail_from, self.mail_to),
                         setting.auto_review_time,  # 审核保存时间
                         setting.auto_review_expire,  # 规则有效时间
                         setting.auto_review_num,  # 连续通过或拒绝次数
                         time.time()])


############################################################
# 线程

# 任务执行线程
def worker(task):
    try:
        p = Processor(task)
        p.run()
    except (DatabaseError, InterfaceError), e:
        #如果报数据库异常，关闭连接，重新处理任务
        outerror('DatabaseError: {}'.format(task))
        outerror(traceback.format_exc())
        connection.close()
        #redis.rpush(MAIL_INCHECK_QUEUE, task)
        gevent.sleep(10)
        return
    except:
        p.handle_error()
        outerror('processor error:{}'.format(task))
        outerror(traceback.format_exc())
    finally:
        p.finish()
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

    pool.join()
    return

############################################################
# 初始化全局变量
def init_resource():
    global domain_blacklist, setting,  recipient_whitelist, attach_type_blacklist, \
       blacklist, recipient_whitelist_domain, sender_whitelist, sender_credit_vals, credit_interval_settings

    blacklist = {
        'keyword_blacklist': Checklist(KeywordBlacklist, type='relay'),
        'subject_blacklist': Checklist(SubjectKeywordBlacklist, type='relay'),
        'attach_blacklist': Checklist(AttachmentBlacklist, type='relay'),
        'sender_blacklist': Checklist(SenderBlacklist, type='relay'),
        'subject_whitelist': Checklist(SubjectKeywordWhitelist, type='relay'),
        'custom_blacklist': Checklist(CustomKeywordBlacklist, type='relay')
    }
    domain_blacklist = DomainBlacklist.objects.filter(disabled=False).values_list('domain', flat=True)
    recipient_whitelist = RecipientWhitelist.objects.filter(disabled=False, is_domain=False).values_list('keyword', flat=True)
    recipient_whitelist_domain = RecipientWhitelist.objects.filter(disabled=False, is_domain=True).values_list('keyword', flat=True)
    attach_type_blacklist = AttachmentTypeBlacklist.objects.filter(disabled=False).values_list('keyword', flat=True)
    sender_whitelist = RelaySenderWhitelist.objects.filter(disabled=False).values_list('sender', flat=True)
    sender_credit_list = SenderCredit.objects.values_list('sender','credit')
    sender_credit_vals = dict(sender_credit_list)
    credit_interval_settings = CreditIntervalSettings.objects.annotate(bulk_sender_time_f=F('bulk_sender_time')*60).\
        values('credit_b', 'credit_e', 'bulk_max', 'bulk_sender_time_f', 'bulk_sender_max')

    domain_blacklist = map(lambda a: a.replace('\r', ''), domain_blacklist)
    attach_type_blacklist = map(lambda a: a.replace('\r', ''), attach_type_blacklist)
    settings = CheckSettings.objects.all()

    if not redis.ttl(MAIL_SUBJECT_HASH):
        redis.expire(MAIL_SUBJECT_HASH, 24 * 60 * 60)

    if settings:
        setting = settings[0]
        setting.max_size *= 1024 * 1024
        setting.sender_max_size *= 1024
        setting.subject_max_size *= 1024
        setting.content_max_size *= 1024
        setting.custom_max_size *= 1024
        setting.spam_max_size *= 1024
        setting.dspam_max_size *= 1024
        setting.ctasd_max_size *= 1024
        setting.attachment_min_size *= 1024
        setting.active_spam_monitor_time *= 60
        setting.active_spam_check_time *= 3600
        setting.bulk_sender_time *= 60
        setting.auto_review_time *= 86400
        setting.auto_review_expire *= 86400
        setting.collect_attachment_min_size *= 1024
        h = int(time.strftime('%H'))
        if h >= 19 or h < 7:
            setting.spam_score_max = setting.night_spam_score_max
            # outinfo('check_setting: bulk_max({}), bulk_expire({}), max_size({}), spam_score_max({})'.format(
            #     setting.bulk_max,
            #     setting.bulk_expire,
            #     setting.max_size,
            #     setting.spam_score_max
            # ))
    for k, v in redis.hgetall(MAIL_BULK_EXPIRE_HASH).iteritems():
        # redis.hset(MAIL_BULK_HASH, k, setting.bulk_max)
        if float(v) + 60 * 60 * 24 * setting.bulk_expire < time.time():
            redis.hdel(MAIL_BULK_EXPIRE_HASH, k)
            redis.hdel(MAIL_BULK_HASH, k)

    do_update_spam_sender(setting)
    global bulk_count
    redis.set(bulk_count_key, bulk_count)

    # for k, v in redis.hgetall(SPAM_SENDER).iteritems():
    #     if float(v) + 60 * 60 * 24 < time.time():
    #         redis.hdel(SPAM_SENDER, k)


def do_update_spam_sender(setting):
    # 不用更新
    if redis.hget(SPAM_SENDER_HISTORY, 'is_need_update') == 'False':
        return

    monitor_time = setting.active_spam_monitor_time
    max = setting.active_spam_max
    check_time = setting.active_spam_check_time
    for k, v in redis.hgetall(SPAM_SENDER_HISTORY).iteritems():
        if k == 'is_need_update':
            continue
        time_list = v.split(',')
        last_time = float(time_list[0].strip())
        now = time.time()
        # 如果超过监测时间 直接清空key
        if now > last_time + check_time:
            redis.hdel(SPAM_SENDER_HISTORY, k)
            redis.hdel(SPAM_SENDER, k)
        elif not redis.hexists(SPAM_SENDER, k) and len(time_list) >= max and float(
                time_list[max - 1]) + monitor_time > now:
            redis.hset(SPAM_SENDER, k, last_time)
    redis.hset(SPAM_SENDER_HISTORY, 'is_need_update', 'False')


def init_resource_routine():
    global bulk_count
    bulk_count = redis.get(bulk_count_key)
    if not bulk_count:
        bulk_count = -1
        redis.set(bulk_count_key, -1)
    bulk_count = int(bulk_count)

    while True:
        try:
            outinfo('init resouce routine')
            init_resource()
        except BaseException as e:
            outerror('init_resource_routine exception')
        gevent.sleep(60)


############################################################

# 信号量处理
def signal_handle(mode):
    outinfo("catch signal: %s" % mode)
    global signal_stop
    signal_stop = True

def init_queue_and_pidfile():
    global MAIL_INCHECK_QUEUE, incheck_pid_file
    if len(sys.argv) > 1:
       MAIL_INCHECK_QUEUE = sys.argv[1]
       incheck_pid_file = MAIL_INCHECK_QUEUE + '.pid'

if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug()
    init_queue_and_pidfile()
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_makedir()
    Common.init_pid_file(incheck_pid_file)
    Common.init_logger(MAIL_INCHECK_QUEUE, len(sys.argv) > 2, _DEBUG)
    clamav_sock = Common.cfgDefault.get('clamav', 'sock')
    review_help_mode = Common.cfgDefault.get('review_help', 'mode')
    init_resource()
    gevent.spawn(init_resource_routine)
    
    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    try:
        # 设置监听信号量
        Common.gevent_signal_init(signal_handle)
        scanner()
    except KeyboardInterrupt:
        signal_handle('sigint')
    except:
        outerror(traceback.format_exc())
        EXIT_CODE = 1
    outinfo("program quit")
    sys.exit(EXIT_CODE)
