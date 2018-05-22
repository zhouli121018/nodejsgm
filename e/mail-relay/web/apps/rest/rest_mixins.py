"""
Basic building blocks for generic class based views.

We don't bind behaviour to http method handlers yet,
which allows mixin classes to be composed in interesting ways.
"""
from __future__ import unicode_literals
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework import mixins
from rest_framework import viewsets

class RestCreateModelMixin(object):
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer_data = serializer.data.copy()
        serializer_data.update({'http_status_code': status.HTTP_200_OK})
        return Response(serializer_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}

class RestRetrieveModelMixin(object):
    """
    Retrieve a model instance.
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data.copy()
        serializer_data.update({'http_status_code': status.HTTP_200_OK})
        return Response(serializer_data)

class RestUpdateModelMixin(object):
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer_data = serializer.data.copy()
        serializer_data.update({'http_status_code': status.HTTP_200_OK})
        return Response(serializer_data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class RestDestroyModelMixin(object):
    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        serializer_data = {'http_status_code': status.HTTP_200_OK}
        return Response(serializer_data)

    def perform_destroy(self, instance):
        instance.delete()

class RestModelViewSet(RestCreateModelMixin,
                   RestRetrieveModelMixin,
                   RestUpdateModelMixin,
                   RestDestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
