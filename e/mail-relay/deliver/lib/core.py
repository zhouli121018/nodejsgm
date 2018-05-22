#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import os
import redis

_config_path_default = os.path.join(os.path.dirname(__file__), '../etc/config.example')
_config_path = os.getenv('PACKAGE_CONFIG', _config_path_default)
_config = ConfigParser.ConfigParser()
_config.read(_config_path)

config = {
    'redis': {
        'host': _config.get('redis', 'host'),
        'port': _config.getint('redis', 'port'),
        'db': _config.getint('redis', 'db')
    },
    'task': {
        'host': _config.get('task', 'host'),
        'port': _config.getint('task', 'port')
    },
    'message_dir': _config.get('deliver', 'message_dir'),
    'greenlet_number': _config.getint('deliver', 'greenlet_number'),
    'connect_time': _config.getint('deliver', 'connect_time'),
    'deliver_time': _config.getint('deliver', 'deliver_time')
}

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)s %(message)s'))

log = logging.getLogger('deliver')
log.addHandler(_handler)
log.setLevel(logging.DEBUG)


def get_redis_cli():
    return redis.StrictRedis(**config['redis'])


def _message_path(mail_ident):
    return os.path.join(config['message_dir'], mail_ident)


def put_message(mail_ident, message):
    with open(_message_path(mail_ident), 'wb') as f:
        f.write(message)


def get_message(mail_ident):
    with open(_message_path(mail_ident), 'rb') as f:
        return f.read()


def del_message(mail_ident):
    try:
        os.remove(_message_path(mail_ident))
    except OSError:
        pass


def message_number():
    return len(os.listdir(config['message_dir']))
