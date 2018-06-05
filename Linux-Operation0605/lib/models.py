# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ZeroDateTimeField(models.DateTimeField):
    def get_db_prep_value(self, value, connection, prepared=False):
        # Casts datetimes into the format expected by the backend
        if not prepared:
            value = self.get_prep_value(value)

        # Use zeroed datetime instead of NULL
        if value is None:
            return "0000-00-00 00:00:00"
        else:
            return connection.ops.adapt_datetimefield_value(value)
            # return connection.ops.value_to_db_datetime(value)

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
            # return connection.ops.value_to_db_datetime(value)