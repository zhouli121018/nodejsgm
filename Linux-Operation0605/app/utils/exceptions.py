# -*- coding: utf-8 -*-
from django.http import HttpResponseForbidden
from django.template import loader
from django.utils.translation import ugettext_lazy as _


# 普通用户
def _requred_forbid(msg):
    t = loader.get_template('perm/perm_404.html')
    content = t.render({'message': msg })
    return HttpResponseForbidden(content)

_html = u"""<html><head><title>403 Forbidden</title></head><body><h1>403 Forbidden</h1><p style="color:red">非常抱歉，您没有访问权限。</p></body></html>"""
_super = _(u'非常抱歉，您没有访问权限。')
_user = _(u'非常抱歉，您没有访问权限。请联系您的管理员！')
superuser_requred_forbid = _requred_forbid(_super)
user_permissions_forbid = _requred_forbid(_user)

