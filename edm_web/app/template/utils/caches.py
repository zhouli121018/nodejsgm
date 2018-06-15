# -*- coding: utf-8 -*-

import json
from django_redis import get_redis_connection

## 模板推送队列
def pushCheck(user_id, template_id):
    redis = get_redis_connection()
    p = redis.pipeline()
    p.rpush('template_check', template_id)
    p.lpush('edm_web_mail_template_point_queue', json.dumps({
        "user_id": user_id,
        'template_id': template_id,
    }))
    p.execute()