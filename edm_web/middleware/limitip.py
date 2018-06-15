# -*- coding: utf-8 -*-
#
"""
 限制IP 请求数量
"""
import re
from django.conf import settings
from django_redis import get_redis_connection
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object
from .errors import limitip_requred_forbid

# 60秒的请求次数
LIMIT_IP_REQUEST = getattr(settings, "LIMIT_IP_REQUEST", 100)
# 60秒的最大请求次数
LIMIT_IP_REQUEST_MOST = getattr(settings, "LIMIT_IP_REQUEST_MOST", 110)
# 请求过期时间
LIMIT_IP_REQUEST_TIMEOUT = getattr(settings, "LIMIT_IP_REQUEST_TIMEOUT", 60)

def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
    else:
        return request.META['REMOTE_ADDR']

# 过滤掉一些请求
path_regex = re.compile(r'(/setting/message/ajax/|' # 站内通知
                        r'/setting/ajax_customer_message/|' # 站内通知
                        r'/wechat/bind_img|' # 微信绑定
                        r'/wechat/bind_wechat/|' # 微信绑定
                        r'/wechat/ajax_check_bind/|' # 微信绑定
                        r'/service/ajax_mail_accurate_open/|' # 精准数据库
                        r'/suggest/ajax/|' # 建议
                        r'/ajax_get_remark_base|'  # 备注
                        r'/template/ajax_check_result_report/|' # 模板检测
                        r'/template/ck/ref/|'  # 引用模板
                        r'/mosaico/img/|'  # 可视化编辑
                        r'/mosaico/start/\d+/img/\w+|' # 可视化编辑
                        r'/address/ajax_count/\d+/|'  # 地址池退订数量加载
                        r'/task/ajax_template_info/\d+/|' # 任务 模板加载
                        r'/template/ajax_get_network_attach/|' # 在线附件下载
                        r'/task/ajax_stat_info/\d+/)', # 任务 统计加载
                        # r'/p/|'  # 在线查看邮件（查看模板）
                        # r'/template/ajax_unsubscribe_or_complaints/|'
                        # r'/new_track/t\d/\w+)', # 跟踪链接
                        flags=re.M)

class LimitIPRequestsMiddleware(MiddlewareMixin):

    def process_request(self, request):
        path = request.path
        if path_regex.match(path):
            return None
        ip = get_ip(request)
        redis = get_redis_connection(alias='limitip')
        if request.user.is_authenticated:
            key1=":edmweb:limitip:request:auth:{}:{}".format(ip, request.user.id)
            if self.limit_request(redis, key1, request_num=LIMIT_IP_REQUEST, timeout=LIMIT_IP_REQUEST_TIMEOUT):
                cnt = redis.get(key1)
                cnt = cnt and int(cnt) or 0
                if request.is_ajax() and cnt<=LIMIT_IP_REQUEST_MOST:
                    return None
                return limitip_requred_forbid
            return None
        key2=":edmweb:limitip:request:authno:%s"%ip
        if self.limit_request(redis, key2, request_num=LIMIT_IP_REQUEST, timeout=LIMIT_IP_REQUEST_TIMEOUT):
            return limitip_requred_forbid

    def limit_request(self, redis, key, request_num=50, timeout=60):
        lua = redis.register_script("""
            local key, amount, limitreq, timeout = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3])
            local cnt, ret
            cnt = redis.call('incrby', key, amount)
            if redis.call('ttl', key) < 0 then
                redis.call('expire', key, timeout)
            end
            if cnt > limitreq then
                ret = true
            else
                ret = false
            end
            return ret
        """)
        return lua(keys=[key],
                   args=[1, request_num, timeout])