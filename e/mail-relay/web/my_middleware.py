# coding=utf-8
from django import http

class ReadOnlyMiddleware(object):
    """
    只读权限的用户 禁用POST
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE') and request.user.has_perm(
                    'core.readonly') and not request.user.is_superuser:
                return http.HttpResponseForbidden('<h1>Forbidden</h1>')
