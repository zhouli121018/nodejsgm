#coding=utf-8
"""
获取postfix　统计状态数据
"""
import os
import datetime
from common import my_grep

def get_postfix_data(date=None):
    log_files = filter(lambda f: f.startswith('postfix'), os.listdir('/var/log/'))

    status_dict = {
        'connect_num': [': connect from', 'postfix'],
        'reject_num': ['Recipient address rejected'],
        'pass_num': ['status=sent (250 Ok)'],
        'rate1': ['Recipient address rejected', 'per 20 minutes'],
        'rate2': ['Recipient address rejected', 'per 30 minutes'],
        'rate3': ['Recipient address rejected', 'per 1 hour'],
        'rate4': ['Recipient address rejected', 'per 3 hour'],
        'rate5': ['Recipient address rejected', 'per 10 minutes'],
        'rate6': ['Recipient address rejected', 'per 6 hour'],
        'rate7': ['Recipient address rejected', 'per 12 hour'],
        'rate8': ['Recipient address rejected', 'per 24 hour'],
        'spf': ['Recipient address rejected', 'spf'],
        'spf_error': ['Recipient address rejected', 'SPF'],
        'rbl': ['Recipient address rejected', 'rbl'],
    }



    res = {}
    if not date:
        date = datetime.date.today()
    date_str = '%s %2d' % (date.strftime('%b'), int(date.strftime('%d')))
    for k, v in status_dict.iteritems():
        v.insert(0, date_str)
        num = 0
        for f in log_files:
            f = '/var/log/{}'.format(f)
            num += my_grep(f, v)
        res[k] = num
    return res


if __name__ == "__main__":
    get_postfix_data()

