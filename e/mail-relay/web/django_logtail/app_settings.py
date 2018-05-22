import os
from django.conf import settings
from apps.core.models import Cluster

LOGTAIL_UPDATE_INTERVAL = getattr(settings, 'LOGTAIL_UPDATE_INTERVAL', '3000')
LOGTAIL_FILES = getattr(settings, 'LOGTAIL_FILES', {})

DEPLOY_DIR = getattr(settings, 'DEPLOY_DIR', '')
# TROY_DIR = getattr(settings, 'TROY_DIR', '')
# MONITOR_DIR = getattr(settings, 'MONITOR_DIR', '')

def get_logtail_files():
    LOGTAIL_FILES = getattr(settings, 'LOGTAIL_FILES', {})
    for c in Cluster.objects.all():
        #LOGTAIL_FILES[c.name] = os.path.join(DEPLOY_DIR, 'log', 'deploy_%s.log' % c.id)
        LOGTAIL_FILES[str(c.id)] = (c.name, os.path.join(DEPLOY_DIR, 'log', 'deploy_%s.log' % c.id))
        # LOGTAIL_FILES['m_{}'.format(c.id)] = (c.name, os.path.join(MONITOR_DIR, 'log', 'monitor_%s.log' % c.id))
    # LOGTAIL_FILES['register'] = (c.name, os.path.join(TROY_DIR, 'log', 'qq_register.log'))
    return LOGTAIL_FILES
