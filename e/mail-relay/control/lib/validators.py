# !/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

import re
import redis
import logging
import time

# from common import outinfo, log.error
log = logging.getLogger('bs_esmtpd')

dns_suffix = [
    'com', 'cn', 'net', 'tw', 'hk', 'co', 'cm', 'om', 'jp', 'org', 'cc', 'uk', 'sg', 'edu', 'au',
    'kr', 'ca', 'fr', 'biz', 'de', 'ru', 'it', 'sh', 'tv', 'vn', 'br', 'my', 'ne', 'nz', 'in',
    'pl', 'info', 'us', 'pk', 'za', 'nl', 'gov', 'ch', 'an', 'se', 'id', 'hu', 'es', 'cz', 'asia',
    'tr', 'ph', 'nt', 'mo', 'dk', 'pt', 'gd', 'et', 'th', 'sn', 'jo', 'gr', 'cq', 'bj', 'be',
    'as', 'ws', 'sz', 'np', 'nc', 'me', 'lk', 'eu', 'ee', 'cr', 'cl', 'bz', 'yu', 'ua', 'tm',
    'tj', 'sd', 'sa', 'ro', 'no', 'mx', 'mk', 'lt', 'ls', 'il', 'ie', 'bg', 'bb', 'az', 'at',
    'ar', 'ae', 'ad', 'ac', 'zm', 'to', 'su', 'sk', 'sj', 'si', 'pf', 'pe', 'mt', 'mm', 'mg',
    'ma', 'lv', 'lb', 'kz', 'ir', 'hr', 'hn', 'gn', 'gh', 'fj', 'cd', 'by', 'bn', 'am', 'aero',
    'zw', 'zr', 'yt', 'yr', 'ye', 'xxx', 'wf', 'vu', 'vi', 'vg', 've', 'vc', 'va', 'uz', 'uy',
    'um', 'ug', 'tz', 'tt', 'travel', 'trav', 'tp', 'tn', 'tl', 'tk', 'tg', 'tf', 'tel', 'td', 'tc',
    'sy', 'sv', 'st', 'sr', 'so', 'sm', 'sl', 'sc', 'sb', 'rw', 're', 'qa', 'py', 'pw', 'ps',
    'pro', 'pr', 'pn', 'pm', 'pg', 'pa', 'nu', 'nr', 'ni', 'ng', 'nf', 'name', 'na', 'mz', 'mw',
    'mv', 'museum', 'mu', 'ms', 'mr', 'mq', 'mp', 'mobi', 'mn', 'ml', 'mil', 'mh', 'md', 'mc', 'ly',
    'lu', 'lr', 'li', 'lc', 'la', 'ky', 'kw', 'kp', 'kn', 'km', 'ki', 'kh', 'kg', 'ke', 'jobs',
    'jm', 'je', 'is', 'iq', 'io', 'int', 'im', 'idv', 'ht', 'hm', 'gy', 'gw', 'gu', 'gt', 'gs',
    'gq', 'gp', 'gm', 'gl', 'gi', 'gg', 'gf', 'ge', 'gb', 'ga', 'fo', 'fm', 'fk', 'fi', 'ev',
    'er', 'eh', 'eg', 'ec', 'dz', 'do', 'dm', 'dj', 'cy', 'cx', 'cv', 'cu', 'coop', 'ck', 'ci',
    'cg', 'cf', 'bw', 'bv', 'bt', 'bs', 'bo', 'bm', 'bi', 'bh', 'bf', 'bd', 'ba', 'aw', 'arpa',
    'areo', 'aq', 'ao', 'al', 'ai', 'ag', 'af', 'top'
]

email_regex = re.compile(r"^(\w|[#&+\-./='])+@\w+([-.]\w+)*\.(\w+)$")


def check_email_format(addr, suffix_list=dns_suffix, is_check_suffix=True):
    re_obj = email_regex.match(addr.lower())
    if not re_obj:
        return False
    if is_check_suffix:
        suffix = re_obj.group(3)
        if not suffix_list:
            suffix_list = dns_suffix

        if suffix not in suffix_list:
            return False

    return True


#def check_address_valid(redis_db, address):
#    return not redis_db.sismember('address_invalid', address)


def check_address_valid(mongodb, address):
    return mongodb['mm-mc'].badmail.find_one({'addr': address.lower()}) is None

def get_addr_domain(addr):
    return addr.split('@')[-1].lower()

def is_same_domain(addr1, addr2):
    return get_addr_domain(addr1) == get_addr_domain(addr2)

class Authentication(object):
    def __init__(self, db_factory, redis_db, use_cache=True, cache_expire=180):
        self.db_factory = db_factory
        self.redis_db = redis_db
        self.use_cache = use_cache
        self.cache_expire = cache_expire

        self.redis_ip_key = 'bs:ip_auth:{ip}'
        self.redis_user_key = 'bs:user_auth:{username}:{password}'
        self.redis_mailbox_key = 'bs:user_auth:{username}'
        self.redis_domain_key = 'bs:domain_auth:{domain}'
        self.redis_collect_domain_key = 'bs:collect_domain_auth:{domain}'


    def get_ip_cache(self, ip):
        if not self.use_cache:
            return None, None

        try:
            key = self.redis_ip_key.format(ip=ip)
            disabled, uid = self.redis_db.hmget(key, ['disabled', 'uid'])
            if disabled in ['0', '1']:
                return disabled, uid
            else:
                return None, None

        except redis.RedisError, e:
            log.error('get ip cache error: %s' % e)
            return None, None


    def get_user_cache(self, username, password):
        if not self.use_cache:
            return None, None
        try:
            password = hashlib.md5(password).hexdigest()
            key = self.redis_user_key.format(username=username, password=password)
            disabled, uid = self.redis_db.hmget(key, ['disabled', 'uid'])
            if disabled in ['0', '1']:
                return disabled, uid
            else:
                return None, None
        except redis.RedisError, e:
            log.error('get user cache error: %s' % e)
            return None, None


    def get_mailbox_cache(self, username):
        if not self.use_cache:
            return None, None
        try:
            key = self.redis_mailbox_key.format(username=username)
            disabled, uid = self.redis_db.hmget(key, ['disabled', 'uid'])
            if disabled in ['0', '1']:
                return disabled, uid
            else:
                return None, None
        except redis.RedisError, e:
            log.error('get user cache error: %s' % e)
            return None, None


    def get_domain_cache(self, domain):
        if not self.use_cache:
            return None, None

        try:
            key = self.redis_domain_key.format(domain=domain)
            disabled, uid = self.redis_db.hmget(key, ['disabled', 'uid'])
            if disabled in ['0', '1']:
                return disabled, uid
            else:
                return None, None

        except redis.RedisError, e:
            log.error('get ip cache error: %s' % e)
            return None, None

    def save_ip_cache(self, ip, uid, disabled):
        if not self.use_cache:
            return

        try:
            key = self.redis_ip_key.format(ip=ip)
            self.redis_db.hmset(key, {'uid': uid, 'disabled': disabled})
            self.redis_db.expire(key, self.cache_expire)
        except redis.RedisError, e:
            log.error('save ip cache error: %s' % e)


    def get_collect_domain_cache(self, domain):
        if not self.use_cache:
            return None, None

        try:
            key = self.redis_collect_domain_key.format(domain=domain)
            disabled, uid = self.redis_db.hmget(key, ['disabled', 'uid'])
            if disabled in ['0', '1']:
                return disabled, uid
            else:
                return None, None

        except redis.RedisError, e:
            log.error('get collect domain cache error: %s' % e)
            return None, None

    def save_user_cache(self, username, password, uid, disabled):
        if not self.use_cache:
            return

        try:
            password = hashlib.md5(password).hexdigest()
            key = self.redis_user_key.format(username=username, password=password)
            self.redis_db.hmset(key, {'uid': uid, 'disabled': disabled})
            self.redis_db.expire(key, self.cache_expire)
        except redis.RedisError, e:
            log.error('save user cache error: %s' % e)

    def save_mailbox_cache(self, username, uid, disabled):
        if not self.use_cache:
            return

        try:
            key = self.redis_mailbox_key.format(username=username)
            self.redis_db.hmset(key, {'uid': uid, 'disabled': disabled})
            self.redis_db.expire(key, self.cache_expire)
        except redis.RedisError, e:
            log.error('save user cache error: %s' % e)


    def save_domain_cache(self, domain, uid, disabled):
        if not self.use_cache:
            return

        try:
            key = self.redis_domain_key.format(domain=domain)
            self.redis_db.hmset(key, {'uid': uid, 'disabled': disabled})
            self.redis_db.expire(key, self.cache_expire)
        except redis.RedisError, e:
            log.error('save domain cache error: %s' % e)

    def save_collect_domain_cache(self, domain, uid, disabled):
        if not self.use_cache:
            return

        try:
            key = self.redis_collect_domain_key.format(domain=domain)
            self.redis_db.hmset(key, {'uid': uid, 'disabled': disabled})
            self.redis_db.expire(key, self.cache_expire)
        except redis.RedisError, e:
            log.error('save domain cache error: %s' % e)

    def auth_by_ip(self, ip):
        disabled, uid = self.get_ip_cache(ip)

        if not disabled:
            rs = self.fetchall_with_retry(
                'select disabled, customer_id from core_customerip where ip=%s and disabled=FALSE',
                (ip,))
            if not rs:
                return False, None
            disabled, uid = rs[0]
            disabled = '1' if disabled else '0'

            self.save_ip_cache(ip, uid, disabled)

        return disabled, uid

    def auth_by_password(self, username, password):
        disabled, uid = self.get_user_cache(username, password)
        if not disabled:
            rs = self.fetchall_with_retry(
                'select disabled, customer_id from core_customermailbox where mailbox=%s and password=%s and disabled=FALSE',
                (username, password))
            if not rs:
                return False, None
            disabled, uid = rs[0]
            disabled = '1' if disabled else '0'

            self.save_user_cache(username, password, uid, disabled)

        return disabled, uid

    def auth_by_domain(self, domain):
        disabled, uid = self.get_domain_cache(domain)

        if not disabled:
            rs = self.fetchall_with_retry(
                'select disabled, customer_id from core_customerdomain where domain=%s and disabled=FALSE',
                (domain.lower(),))
            if not rs:
                return False, None
            disabled, uid = rs[0]
            disabled = '1' if disabled else '0'

            self.save_domain_cache(domain, uid, disabled)

        return disabled, uid

    def auth_by_collect_domain(self, domain):
        disabled, uid = self.get_collect_domain_cache(domain)

        if not disabled:
            rs = self.fetchall_with_retry(
                'select disabled, customer_id from core_colcustomerdomain where domain=%s',
                (domain.lower(),))
            if not rs:
                return False, None
            disabled, uid = rs[0]
            #disabled = '1' if disabled else '0'
            disabled = '0'

            self.save_collect_domain_cache(domain, uid, disabled)

        return disabled, uid

    def auth_by_mailbox(self, username):
        disabled, uid = self.get_mailbox_cache(username)
        if not disabled:
            rs = self.fetchall_with_retry(
                'select disabled, customer_id from core_customermailbox where mailbox=%s and disabled=FALSE',
                (username,))
            if not rs:
                return False, None
            disabled, uid = rs[0]
            disabled = '1' if disabled else '0'

            self.save_mailbox_cache(username, uid, disabled)

        return disabled, uid

    def fetchall_with_retry(self, operation, parameters):
        while True:
            try:
                with self.db_factory.cursor() as cur:
                    cur.execute(operation, parameters)
                    return cur.fetchall()
            except BaseException as e:
                self.db_factory.close()
                log.error('fetch_with_rety: %s' % e)
                time.sleep(1)
