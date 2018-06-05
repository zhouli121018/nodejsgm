# -*- coding: utf-8 -*-
from functools import wraps
from .exceptions import superuser_requred_forbid

def superuser_required(func):
    @wraps(func)
    def decorate(request, *args, **kwargs):
        if request.user.is_superuser:
            return func(request, *args, **kwargs)
        return superuser_requred_forbid
    return decorate

