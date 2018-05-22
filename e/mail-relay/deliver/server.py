#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent.monkey

gevent.monkey.patch_all()

import flask
import gevent.wsgi
import gevent.lock
import hashlib
import json
import struct
import zlib

from lib.core import log, get_redis_cli, put_message, message_number
from lib.models import deliver_model

redis_cli = get_redis_cli()
app = flask.Flask(__name__)
lock = gevent.lock.RLock()


def unpack_deliver(body):
    # body structure:
    #   json_size, compressed_size
    #   message_md5
    #   json_data
    #   compressed_data

    json_size, compressed_size = struct.unpack('!QQ', body[:16])
    json_data = body[32:32 + json_size]
    d = deliver_model.load(json.loads(json_data))
    compressed_data = body[32 + json_size:]
    assert len(compressed_data) == compressed_size
    message = zlib.decompress(compressed_data)
    md5 = hashlib.md5()
    md5.update(message)
    assert md5.digest() == body[16:32]

    return d, message


@app.route('/deliver/', methods=['put'])
def receive():
    """
    接收一封邮件
    """

    d, message = unpack_deliver(flask.request.data)

    with lock:
        if not redis_cli.hexists('detail', d['mail_ident']):
            put_message(d['mail_ident'], message)
            (redis_cli.pipeline()
             .lpush('received', d['mail_ident'])
             .hset('detail', d['mail_ident'], json.dumps(d))
             .execute())
            log.info(u'receive: mail_ident={mail_ident}'.format(**d))
        else:
            log.warning(u'receive: mail_ident={mail_ident} already exist'.format(**d))

    return ''


@app.route('/state/')
def state():
    pipe = redis_cli.pipeline()
    pipe.hlen('detail')
    for key in ['received', 'waiting', 'retry_waiting', 'delivered'] + ['logging_{}'.format(i) for i in xrange(10)]:
        pipe.llen(key)
    r = pipe.execute()

    d = {
        'message_number': message_number(),
        'detail': r[0],
        'received': r[1],
        'waiting': r[2],
        'retry_waiting': r[3],
        'delivered': r[4],
        'logging': sum(r[5:])
    }

    return json.dumps(d)


def main():
    global all_routine

    all_routine = [gevent.spawn(gevent.wsgi.WSGIServer(('0.0.0.0', port), app).serve_forever)
                   for port in (80, 88, 10001)]
    gevent.joinall(all_routine)


if __name__ == '__main__':
    main()
