#!coding=utf-8
from django.db import models

class ZeroDateField(models.DateField):
    def get_db_prep_value(self, value, connection, prepared=False):
        # Casts datetimes into the format expected by the backend
        if not prepared:
            value = self.get_prep_value(value)

        # Use zeroed datetime instead of NULL
        if value is None:
            return "0000-00-00"
        else:
            return connection.ops.adapt_datetimefield_value(value)

class CharBooleanField(models.BooleanField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        super(CharBooleanField, self).__init__(*args, **kwargs)

    """
    def get_prep_value(self, value):
        if value:
            return '-1'
        else:
            return '1'
    """
