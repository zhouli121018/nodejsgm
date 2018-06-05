# -*- coding: utf-8 -*-

from django.utils.deprecation import MiddlewareMixin
from ..exceptions import user_permissions_forbid
from ..regex import path_sub
from app.perm.models import MyPermission

class PermissionsMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        if request.is_ajax() and request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return None
        uri = path_sub(request.path)
        permobj = MyPermission.objects.filter(url=uri).first()
        if not permobj:
            return None
        perm = permobj.get_perm()
        if not request.user.has_perm(perm):
            return user_permissions_forbid
        return None
