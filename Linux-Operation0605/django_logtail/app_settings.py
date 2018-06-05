# -*- coding: utf-8 -*-
#
import os
from django.conf import settings
from django_sysinfo.conf import PROCESSES

LOGTAIL_UPDATE_INTERVAL = getattr(settings, 'LOGTAIL_UPDATE_INTERVAL', '3000')


LOGTAIL_FILES = {
    'update_umail_beta': os.path.join(settings.BASE_DIR, 'log', 'update_umail_beta.log' )
}

for k, v in PROCESSES.iteritems():
    filepath = v.get('log', '')
    if os.path.exists(filepath):
        LOGTAIL_FILES[k] = filepath
