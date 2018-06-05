# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

import uuid
import json
import random
from django_redis import get_redis_connection


def proxy_server_redis(protocol=None, master_id=None):
    task_id = "{:0>5d}-{}".format(random.randint(1, 10000), uuid.uuid1())
    task_data = {
        "protocol" :   protocol,
        "data": master_id and { "master_id": master_id } or {}
    }

    redis = get_redis_connection()
    redis.hset( "task_data:proxy_web_command", task_id, json.dumps(task_data) )
    redis.rpush( "task_queue:proxy_web_command", task_id )
