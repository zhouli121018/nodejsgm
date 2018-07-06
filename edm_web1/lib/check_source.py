# coding=utf-8
import re
import logging
import traceback

# 关键字检查类
class Checklist(object):
    def __init__(self, model=None, key=''):
        self.model = model
        self.key = key
        if key:
            lists = model.objects.filter(disabled=False, filter_type=key).values_list('keyword', 'is_regex')
        else:
            lists = model.objects.filter(disabled=False).values_list('keyword', 'is_regex')

        self.list = self._init_list(lists)

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

    def search(self, s):
        lists = self.list
        if not s and not self.key:
            return False, False
        for k, is_regex in lists:
            if is_regex:
                r = k.search(s)
                if r:
                    return k.pattern, r.group(0)
            else:
                if s.find(k) != -1:
                    return k, k
        return False, False

