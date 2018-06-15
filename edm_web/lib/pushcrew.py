#coding=utf-8

import json
from django_redis import get_redis_connection


# 推入队列进行 PushCrew 通知
def pushcrew_notice(action, title, message, url=u"https://www.bestedm.org", customer_id=None):
    j = {
        "action": action,
        "title": title,
        "message": message,
        "url": url,
    }
    redis = get_redis_connection()
    redis.lpush("pushcrew:notice", json.dumps(j))

    # 支付宝注册完善资料， 支付宝注册删除key
    if customer_id:
        redis.hdel("pushcrew:zhifubao:register", customer_id)

