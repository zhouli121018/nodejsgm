# -*- coding: utf-8 -*-
#
"""
http://blog.csdn.net/u011628250/article/details/73526390
http://www.anti-abuse.org/multi-rbl-check/
http://www.intel-mail.com/page89?article_id=15
http://www.voidcn.com/article/p-xqnwmdop-cz.html

http://multirbl.valli.org/detail/bl.spamcannibal.org.html
http://support.huawei.com/huaweiconnect/enterprise/thread-294455-1-1.html
https://www.emailcamel.org/node/25
"""

RBL_SEARCH_DOMAINS = [
    (9, "sbl.spamhaus.org", ["127.0.0.2", "127.0.0.3"], "Spamhaus SBL"),
    (10, "xbl.spamhaus.org", ["127.0.0.4", "127.0.0.5", "127.0.0.6", "127.0.0.7"], "Spamhaus XBL"),
    (11, "pbl.spamhaus.org", ["127.0.0.10", "127.0.0.11"], "Spamhaus PBL"),
    (12, "zen.spamhaus.org", ["127.0.0.{}".format(i) for i in range(2, 12)], "Spamhaus ZEN"),
]

RBL_SEARCH_DOMAINS2 = [
    (1, "cbl.abuseat.org", "127.0.0.2", "Abuseat CBL"),
    (2, "bl.spamcop.net", "127.0.0.2", "Spamcop BL"),
    (3, "ix.dnsbl.manitu.net", "127.0.0.2", "Manitu IX"),
    (4, "b.barracudacentral.org", "127.0.0.2", "Barracudacentral B"),
    (5, "l2.apews.org", "127.0.0.2", "Apews 2 L2"),
    (6, "dnsbl-1.uceprotect.net", "127.0.0.2", "Uceprotect -1"),
    (7, "dnsbl-2.uceprotect.net", "127.0.0.2", "Uceprotect -2"),
    (8, "dnsbl-3.uceprotect.net", "127.0.0.2", "Uceprotect -3"),
    (13, "cbl.anti-spam.org.cn", "127.0.8.2", "Anti-spam Cn CBL"),
    (14, "cblplus.anti-spam.org.cn", "127.0.8.2", "Anti-spam Cn CBLPLUS"),
    (15, "cblless.anti-spam.org.cn", "127.0.8.2", "Anti-spam Cn CBLLESS"),
    (16, "backscatter.spameatingmonkey.net", "127.0.0.2", "Spameatingmonkey BL"),
    (17, "ips.backscatterer.org", "127.0.0.2", "Backscatterer IPS"),
    (18, "dnsbl.justspam.org", "127.0.0.2", "Justspam"),
    (19, "hostkarma.junkemailfilter.com", "127.0.0.2", "Junkemailfilter Com HOSTKARMA"),
    (20, "psbl.surriel.com", "127.0.0.2", "Surriel Com PSBL"),
    (21, "spam.dnsbl.anonmails.de", "127.0.0.2", "Anonmails De SPAM"),
    (22, "rbl.abuse.ro", "127.0.0.2", "Abuse Ch SPAM"),
    (23, "dnsbl.sorbs.net", "127.0.0.2", "Sorbs"),
    (24, "dul.dnsbl.sorbs.net", "127.0.0.2", "Sorbs DUL"),
    (25, "db.wpbl.info", "127.0.0.2", "Wpbl Info DB"),
    (26, "dnsbl.inps.de", "127.0.0.2", "Inps De"),
    (27, "bl.mailspike.net", "127.0.0.2", "Mailspike BL"),
    (28, "virbl.dnsbl.bit.nl", "127.0.0.2", "Bit Nl VIRBL"),
]