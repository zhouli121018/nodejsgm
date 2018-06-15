# -*- coding: utf-8 -*-
from django.http import HttpResponseForbidden
from django.template import loader
from django.utils.translation import ugettext_lazy as _


# 普通用户
def _requred_forbid(msg):
    t = loader.get_template('limit_ip.html')
    content = t.render({'message': msg })
    return HttpResponseForbidden(content)

_msg = _(u'请求太频繁，请等待30s后重试(Request too often)。')
limitip_requred_forbid = _requred_forbid(_msg)

