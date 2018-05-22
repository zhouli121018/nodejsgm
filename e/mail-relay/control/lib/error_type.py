# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from apps.flag.models import NotExistFlag, BigQuotaFlag, SpamFlag, NotRetryFlag, SpfFlag, GreyListFlag


def load_error_type_resource():
    global not_exist_flag_list, big_quota_flag_list, spam_flag_list, not_retry_flag_list, spf_flag_list, greylist_flag_list

    not_exist_flag_list = list(NotExistFlag.objects.filter(relay=True).values_list('keyword', flat=True))
    big_quota_flag_list = list(BigQuotaFlag.objects.filter(relay=True).values_list('keyword', flat=True))
    spam_flag_list = list(SpamFlag.objects.filter(relay=True).values_list('keyword', flat=True))
    not_retry_flag_list = list(NotRetryFlag.objects.filter(relay=True).values_list('keyword', flat=True))
    spf_flag_list = list(SpfFlag.objects.filter(relay=True).values_list('keyword', flat=True))
    greylist_flag_list = list(GreyListFlag.objects.filter(relay=True).values_list('keyword', flat=True))


def c_load_error_type_resource():
    global c_not_exist_flag_list, c_big_quota_flag_list, c_spam_flag_list, c_not_retry_flag_list, c_spf_flag_list

    c_not_exist_flag_list = list(NotExistFlag.objects.filter(collect=True).values_list('keyword', flat=True))
    c_big_quota_flag_list = list(BigQuotaFlag.objects.filter(collect=True).values_list('keyword', flat=True))
    c_spam_flag_list = list(SpamFlag.objects.filter(collect=True).values_list('keyword', flat=True))
    c_not_retry_flag_list = list(NotRetryFlag.objects.filter(collect=True).values_list('keyword', flat=True))
    c_spf_flag_list = list(SpfFlag.objects.filter(collect=True).values_list('keyword', flat=True))


def get_error_type(return_code, return_message):
    if check_error_type(return_message, greylist_flag_list):
        return 9
    elif check_error_type(return_message, not_exist_flag_list):
        return 2
    elif check_error_type(return_message, big_quota_flag_list):
        return 4
    elif check_error_type(return_message, spam_flag_list):
        return 5
    elif check_error_type(return_message, spf_flag_list):
        return 7
    elif check_error_type(return_message, not_retry_flag_list):
        return 6
    else:
        if return_code == -1:
            if u'deliver timeout' in return_message:
                return 8
            else:
                return 1
        else:
            return 3


def c_get_error_type(return_code, return_message):
    if check_error_type(return_message, c_not_exist_flag_list):
        return 2
    elif check_error_type(return_message, c_big_quota_flag_list):
        return 4
    elif check_error_type(return_message, c_spam_flag_list):
        return 5
    elif check_error_type(return_message, c_spf_flag_list):
        return 7
    elif check_error_type(return_message, c_not_retry_flag_list):
        return 6
    else:
        if return_code == -1:
            return 1
        else:
            return 3


def c_retry_q(error_type):
    return error_type not in (2, 4, 5, 6)


def check_error_type(message, flag_list):
    for k in flag_list:
        if re.search(k, message, re.IGNORECASE):
            return True
    return False
