# -*- coding: utf-8 -*-
import re


def path_sub(url):
    if re.search(r'(\/\d+?\/)', url):
        url = re.sub(r'(\/\d+?\/)', '/modify/', url)
    return url

pure_digits_regex = lambda s: re.compile('^\d+$').match(s)
pure_english_regex = lambda s: re.compile('^[\.\_\-A-Za-z0-9_]+$').match(s)
pure_email_regex = lambda s: re.compile('^(\w|[-+=.])+@\w+([-.]\w+)*\.(\w+)$').match(s)
pure_ip_regex = lambda s: re.compile('^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$').match(s)
pure_ipaddr_regex = lambda s: re.compile('^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\/(\d+)$').match(s)