# -*- coding: utf-8 -*-

def get_unique_method_id(view_method, request):
    # todo: test me as UniqueMethodIdKeyBit
    return "%s|%s" % (view_method.__name__, request.path.replace('/', '|'))
    # return u'.'.join([
    #     view_instance.__module__,
    #     view_instance.__class__.__name__,
    #     view_method.__name__
    # ])

def get_unique_method_id2(view_method, path):
    # todo: test me as UniqueMethodIdKeyBit
    return "%s|%s" % (view_method, path.replace('/', '|'))

class KeyBitBase(object):
    def __init__(self, params=None):
        self.params = params

    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        """
        @rtype: dict
        """
        raise NotImplementedError()