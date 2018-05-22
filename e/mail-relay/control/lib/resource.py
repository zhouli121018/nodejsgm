# -*-coding:utf8-*-
import re
import logging
import traceback


# 关键字检查类
class Checklist(object):
    def __init__(self, model, type='collect'):
        self.model = model

        if type == 'collect':
            list_tmp = model.objects.filter(collect=True, c_direct_reject=False).values_list('keyword', 'is_regex')
            list_dr_tmp = model.objects.filter(collect=True, c_direct_reject=True).values_list('keyword', 'is_regex')
        else:
            list_tmp = model.objects.filter(relay=True, direct_reject=False).values_list('keyword', 'is_regex')
            list_dr_tmp = model.objects.filter(relay=True, direct_reject=True).values_list('keyword', 'is_regex')

        self.list = self._init_list(list_tmp)
        self.list_dr = self._init_list(list_dr_tmp)

    def _init_list(self, lists):
        res = []
        for keyword, is_regex in lists:
            if is_regex:
                try:
                    r = re.compile(keyword, re.IGNORECASE | re.UNICODE)
                    res.append([r, is_regex])
                except Exception as e:
                    logging.error(u'illegal regular expression: {!r}'.format(keyword))
                    logging.error(traceback.format_exc())
            else:
                res.append([keyword, is_regex])
        return res

    def search(self, s, is_dr=False):
        lists = self.list_dr if is_dr else self.list
        for k, is_regex in lists:
            if is_regex:
                r = k.search(s)
                if r:
                    return k.pattern, r.group(0)
            else:
                if s.find(k) != -1:
                    return k, k
        return False, False


# 发件人白名单，黑名单检测类
class SenderChecklist(object):
    def __init__(self, model):
        self.model = model
        self.list = self._init_list()
        self.msg_dict = {0: u'全局', 'is_domain': u'域'}

    def _init_list(self):
        lists = self.model.objects.filter(disabled=False, is_global=False).values_list('customer_id', 'sender',
                                                                                       'is_domain', 'is_regex')
        res = {}
        for customer_id, sender, is_domain, is_regex in lists:
            key = sender
            if is_regex:
                try:
                    key = re.compile(sender, re.IGNORECASE | re.UNICODE)
                except Exception as e:
                    logging.error(u'illegal regular expression: {!r}'.format(sender))
                    logging.error(traceback.format_exc())
                    continue
            domian_key = 'is_domain' if is_domain else 'not_domain'
            res.setdefault(customer_id, {}).setdefault(domian_key, []).append([key, is_regex])

        res[0] = {}
        lists = self.model.objects.filter(disabled=False, is_global=True).values_list('sender', 'is_domain', 'is_regex')

        for sender, is_domain, is_regex in lists:
            key = sender
            if is_regex:
                try:
                    key = re.compile(sender, re.IGNORECASE | re.UNICODE)
                except Exception as e:
                    logging.error(u'illegal regular expression: {!r}'.format(sender))
                    logging.error(traceback.format_exc())
                    continue
            domain_key = 'is_domain' if is_domain else 'not_domain'
            res[0].setdefault(domain_key, []).append([key, is_regex])
        return res


    def search(self, uid, sender):
        uid = int(uid)
        sender = sender.lower()
        if '=' in sender:
            sender = sender.split('=')[-1]
        domain = sender.split('@')[-1]

        for customer_id, res in self.list.iteritems():
            if customer_id not in [0, uid]:
                continue
            for domain_key, regex_list in res.iteritems():
                s = domain if domain_key == 'is_domain' else sender
                msg = u'{}{}'.format(self.msg_dict.get(customer_id, u'客户'), self.msg_dict.get(domain_key, ''))
                for k, is_regex in regex_list:
                    if is_regex:
                        r = k.search(s)
                        if r:
                            return True, u'{}({}----{})'.format(msg, k.pattern, r.group(0))
                    else:
                        if s.find(k) != -1:
                            return True, u'{}({}----{})'.format(msg, k, s)
        return False, ''


class RegexChecklist(object):

    def __init__(self, model):
        self.model = model
        self.lists = self._init_list()

    def _init_list(self):
        res = []
        lists = self.model.objects.filter(disabled=False).values_list('keyword', 'is_regex')
        for keyword, is_regex in lists:
            if is_regex:
                try:
                    r = re.compile(keyword, re.IGNORECASE | re.UNICODE)
                    res.append([r, is_regex])
                except Exception as e:
                    logging.error(u'illegal regular expression: {!r}'.format(keyword))
                    logging.error(traceback.format_exc())
            else:
                res.append([keyword, is_regex])
        return res

    def search(self, s):
        for k, is_regex in self.lists:
            if is_regex:
                r = k.search(s)
                if r:
                    return k.pattern, r.group(0)
            else:
                if s.find(k) != -1:
                    return k, k
        return False, False


