# -*- coding: utf-8 -*-
#
import re
from app.core.utils import domaintools

domain_regex = re.compile(ur'\w*.?(.com.cn|.gov.cn|.net.cn|.org.cn|.ac.cn|.com.au)$', flags=re.IGNORECASE)

def parse_domain(domain, action='main'):
    d = domaintools.Domain(domain)
    try:
        if action=='main':
            return d.domain
        else:
            return d.subdomain
    except:
        m = domain_regex.search(domain)
        lists = domain.split('.')
        length = len(lists)
        if action=='main':
            return m and '.'.join(lists[length-3:]) or '.'.join(lists[length-2:])
        else:
            return m and '.'.join(lists[:length-3]) or '.'.join(lists[:length-2])
