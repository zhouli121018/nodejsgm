#-*- coding: utf8 -*-

import pymongo

# mongo -u mm-mc -p PFBgatL4Vq63sEP  192.168.50.51/mm-mc
local_mongo_cfg = {
    'host': '192.168.50.51',
    'port': 27017,
    'username': 'mm-mc',
    'dbname': 'mm-mc',
    'password': 'PFBgatL4Vq63sEP',
}
local_mongo = pymongo.MongoClient(host='mongodb://{username}:{password}@{host}:{port}/{dbname}'.format(**local_mongo_cfg))

# mongo -u mm-mc -p PFBgatL4Vq63sEP 192.168.50.64/mm-mc
remote_mongo_cfg = {
    'host': '192.168.50.64',
    'port': 27017,
    'username': 'mm-mc',
    'dbname': 'mm-mc',
    'password': 'PFBgatL4Vq63sEP',
}
remote_mongo = pymongo.MongoClient(host='mongodb://{username}:{password}@{host}:{port}/{dbname}'.format(**remote_mongo_cfg))