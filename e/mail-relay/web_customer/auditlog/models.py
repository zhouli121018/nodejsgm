from __future__ import unicode_literals

import json
import ast

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import QuerySet, Q
from django.utils import formats
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.six import iteritems, integer_types
from django.utils.translation import ugettext_lazy as _

from jsonfield.fields import JSONField
from dateutil import parser


class LogEntryManager(models.Manager):
    """
    Custom manager for the :py:class:`LogEntry` model.
    """

    def log_create(self, instance, **kwargs):
        """
        Helper method to create a new log entry. This method automatically populates some fields when no explicit value
        is given.

        :param instance: The model instance to log a change for.
        :type instance: Model
        :param kwargs: Field overrides for the :py:class:`LogEntry` object.
        :return: The new log entry or `None` if there were no changes.
        :rtype: LogEntry
        """
        changes = kwargs.get('changes', None)
        pk = self._get_pk_value(instance)

        if changes is not None:
            content_type = ContentType.objects.get_for_model(instance)
            kwargs.setdefault('content_type', content_type)
            kwargs.setdefault('object_pk', pk)
            kwargs.setdefault('object_repr', smart_text(instance))
            from auditlog.registry import auditlog
            model_fields = auditlog.get_model_fields(instance._meta.model)
            if model_fields['relate_field']:
                relate_object = getattr(instance, model_fields['relate_field'])
                kwargs.setdefault('relate_id', relate_object.pk)
                kwargs.setdefault('relate_content_type', ContentType.objects.get_for_model(relate_object))
                print 'relate_field', getattr(instance, model_fields['relate_field'])
            else:
                kwargs.setdefault('relate_id', pk)
                kwargs.setdefault('relate_content_type', content_type)


            if isinstance(pk, integer_types):
                kwargs.setdefault('object_id', pk)

            get_additional_data = getattr(instance, 'get_additional_data', None)
            if callable(get_additional_data):
                kwargs.setdefault('additional_data', get_additional_data())

            # Delete log entries with the same pk as a newly created model. This should only be necessary when an pk is
            # used twice.
            if kwargs.get('action', None) is LogEntry.Action.CREATE:
                if kwargs.get('object_id', None) is not None and self.filter(content_type=kwargs.get('content_type'), object_id=kwargs.get('object_id')).exists():
                    self.filter(content_type=kwargs.get('content_type'), object_id=kwargs.get('object_id')).delete()
                else:
                    self.filter(content_type=kwargs.get('content_type'), object_pk=kwargs.get('object_pk', '')).delete()
            # save LogEntry to same database instance is using
            db = instance._state.db
            return self.create(**kwargs) if db is None or db == '' else self.using(db).create(**kwargs)
        return None

    def get_for_object(self, instance):
        """
        Get log entries for the specified model instance.

        :param instance: The model instance to get log entries for.
        :type instance: Model
        :return: QuerySet of log entries for the given model instance.
        :rtype: QuerySet
        """
        # Return empty queryset if the given model instance is not a model instance.
        if not isinstance(instance, models.Model):
            return self.none()

        content_type = ContentType.objects.get_for_model(instance.__class__)
        pk = self._get_pk_value(instance)

        if isinstance(pk, integer_types):
            return self.filter(content_type=content_type, object_id=pk)
        else:
            return self.filter(content_type=content_type, object_pk=smart_text(pk))

    def get_for_objects(self, queryset):
        """
        Get log entries for the objects in the specified queryset.

        :param queryset: The queryset to get the log entries for.
        :type queryset: QuerySet
        :return: The LogEntry objects for the objects in the given queryset.
        :rtype: QuerySet
        """
        if not isinstance(queryset, QuerySet) or queryset.count() == 0:
            return self.none()

        content_type = ContentType.objects.get_for_model(queryset.model)
        primary_keys = list(queryset.values_list(queryset.model._meta.pk.name, flat=True))

        if isinstance(primary_keys[0], integer_types):
            return self.filter(content_type=content_type).filter(Q(object_id__in=primary_keys)).distinct()
        elif isinstance(queryset.model._meta.pk, models.UUIDField):
            primary_keys = [smart_text(pk) for pk in primary_keys]
            return self.filter(content_type=content_type).filter(Q(object_pk__in=primary_keys)).distinct()
        else:
            return self.filter(content_type=content_type).filter(Q(object_pk__in=primary_keys)).distinct()

    def get_for_model(self, model):
        """
        Get log entries for all objects of a specified type.

        :param model: The model to get log entries for.
        :type model: class
        :return: QuerySet of log entries for the given model.
        :rtype: QuerySet
        """
        # Return empty queryset if the given object is not valid.
        if not issubclass(model, models.Model):
            return self.none()

        content_type = ContentType.objects.get_for_model(model)

        return self.filter(content_type=content_type)

    def _get_pk_value(self, instance):
        """
        Get the primary key field value for a model instance.

        :param instance: The model instance to get the primary key for.
        :type instance: Model
        :return: The primary key value of the given model instance.
        """
        pk_field = instance._meta.pk.name
        pk = getattr(instance, pk_field, None)

        # Check to make sure that we got an pk not a model object.
        if isinstance(pk, models.Model):
            pk = self._get_pk_value(pk)
        return pk

    def get_for_relate_object(self, instance):
        """
        Get log entries for the specified model instance.

        :param instance: The model instance to get log entries for.
        :type instance: Model
        :return: QuerySet of log entries for the given model instance.
        :rtype: QuerySet
        """
        # Return empty queryset if the given model instance is not a model instance.
        if not isinstance(instance, models.Model):
            return self.none()

        content_type = ContentType.objects.get_for_model(instance.__class__)
        pk = self._get_pk_value(instance)

        if isinstance(pk, integer_types):
            return self.filter(relate_content_type=content_type, relate_id=pk)
        else:
            return self.filter(relate_content_type=content_type, object_pk=smart_text(pk))

    def get_for_relate_objects(self, queryset):
        """
        Get log entries for the objects in the specified queryset.

        :param queryset: The queryset to get the log entries for.
        :type queryset: QuerySet
        :return: The LogEntry objects for the objects in the given queryset.
        :rtype: QuerySet
        """
        if not isinstance(queryset, QuerySet) or queryset.count() == 0:
            return self.none()

        content_type = ContentType.objects.get_for_model(queryset.model)
        primary_keys = list(queryset.values_list(queryset.model._meta.pk.name, flat=True))

        if isinstance(primary_keys[0], integer_types):
            return self.filter(relate_content_type=content_type).filter(Q(relate_id__in=primary_keys)).distinct()
        elif isinstance(queryset.model._meta.pk, models.UUIDField):
            primary_keys = [smart_text(pk) for pk in primary_keys]
            return self.filter(relate_content_type=content_type).filter(Q(object_pk__in=primary_keys)).distinct()
        else:
            return self.filter(relate_content_type=content_type).filter(Q(object_pk__in=primary_keys)).distinct()

    def get_for_relate_model(self, model):
        """
        Get log entries for all objects of a specified type.

        :param model: The model to get log entries for.
        :type model: class
        :return: QuerySet of log entries for the given model.
        :rtype: QuerySet
        """
        # Return empty queryset if the given object is not valid.
        if not issubclass(model, models.Model):
            return self.none()

        content_type = ContentType.objects.get_for_model(model)

        return self.filter(relate_content_type=content_type)

@python_2_unicode_compatible
class LogEntry(models.Model):
    """
    Represents an entry in the audit log. The content type is saved along with the textual and numeric (if available)
    primary key, as well as the textual representation of the object when it was saved. It holds the action performed
    and the fields that were changed in the transaction.

    If AuditlogMiddleware is used, the actor will be set automatically. Keep in mind that editing / re-saving LogEntry
    instances may set the actor to a wrong value - editing LogEntry instances is not recommended (and it should not be
    necessary).
    """

    class Action:
        """
        The actions that Auditlog distinguishes: creating, updating and deleting objects. Viewing objects is not logged.
        The values of the actions are numeric, a higher integer value means a more intrusive action. This may be useful
        in some cases when comparing actions because the ``__lt``, ``__lte``, ``__gt``, ``__gte`` lookup filters can be
        used in queries.

        The valid actions are :py:attr:`Action.CREATE`, :py:attr:`Action.UPDATE` and :py:attr:`Action.DELETE`.
        """
        CREATE = 0
        UPDATE = 1
        DELETE = 2

        choices = (
            (CREATE, _("create")),
            (UPDATE, _("update")),
            (DELETE, _("delete")),
        )

    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, related_name='+', verbose_name=_("content type"))
    object_pk = models.CharField(db_index=True, max_length=255, verbose_name=_("object pk"))
    object_id = models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name=_("object id"))
    object_repr = models.TextField(verbose_name=_("object representation"))
    action = models.PositiveSmallIntegerField(choices=Action.choices, verbose_name=_("action"))
    changes = models.TextField(blank=True, verbose_name=_("change message"))
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("actor"), db_column='c_actor_id')
    remote_addr = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("remote address"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("timestamp"))
    additional_data = JSONField(blank=True, null=True, verbose_name=_("additional data"))
    relate_content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True, related_name='relate+', verbose_name=_("relate content type"))
    relate_id = models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name=_("relate object id"))
    #c_actor_id = models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name=_("customer actoer id"))
    objects = LogEntryManager()

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")

    def __str__(self):
        if self.action == self.Action.CREATE:
            fstring = _("Created {repr:s}")
        elif self.action == self.Action.UPDATE:
            fstring = _("Updated {repr:s}")
        elif self.action == self.Action.DELETE:
            fstring = _("Deleted {repr:s}")
        else:
            fstring = _("Logged {repr:s}")

        return fstring.format(repr=self.object_repr)

    @property
    def relate_obj(self):
        """
        :return: The relate object.
        """
        return self.relate_content_type.get_object_for_this_type(pk=self.relate_id)

    @property
    def model_class(self):
        """
        :return: The relate object.
        """
        return self.content_type.model_class()._meta.verbose_name.title()

    @property
    def changes_dict(self):
        """
        :return: The changes recorded in this log entry as a dictionary object.
        """
        try:
            return json.loads(self.changes)
        except ValueError:
            return {}

    @property
    def changes_str(self, colon=': ', arrow=smart_text(' \u2192 '), separator='; '):
        """
        Return the changes recorded in this log entry as a string. The formatting of the string can be customized by
        setting alternate values for colon, arrow and separator. If the formatting is still not satisfying, please use
        :py:func:`LogEntry.changes_dict` and format the string yourself.

        :param colon: The string to place between the field name and the values.
        :param arrow: The string to place between each old and new value.
        :param separator: The string to place between each field.
        :return: A readable string of the changes in this log entry.
        """
        substrings = []

        for field, values in iteritems(self.changes_dict):
            substring = smart_text('{field_name:s}{colon:s}{old:s}{arrow:s}{new:s}').format(
                field_name=field,
                colon=colon,
                old=values[0],
                arrow=arrow,
                new=values[1],
            )
            substrings.append(substring)

        return separator.join(substrings)

    @property
    def changes_display_dict(self):
        """
        :return: The changes recorded in this log entry intended for display to users as a dictionary object.
        """
        # Get the model and model_fields
        from auditlog.registry import auditlog
        model = self.content_type.model_class()
        model_fields = auditlog.get_model_fields(model._meta.model)
        changes_display_dict = {}
        # grab the changes_dict and iterate through
        for field_name, values in iteritems(self.changes_dict):
            # try to get the field attribute on the model
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist:
                changes_display_dict[field_name] = values
                continue
            values_display = []
            # handle choices fields and Postgres ArrayField to get human readable version
            try:
                choices = field.choices
            except AttributeError:
                continue
            if choices or hasattr(field, 'base_field') and getattr(field.base_field, 'choices', False):
                choices_dict = dict(field.choices or field.base_field.choices)
                for value in values:
                    try:
                        value = ast.literal_eval(value)
                        if type(value) is [].__class__:
                            values_display.append(', '.join([choices_dict.get(val, 'None') for val in value]))
                        else:
                            values_display.append(choices_dict.get(value, 'None'))
                    except ValueError:
                        values_display.append(choices_dict.get(value, 'None'))
                    except:
                        values_display.append(choices_dict.get(value, 'None'))
            else:
                field_type = field.get_internal_type()
                for value in values:
                    # handle case where field is a datetime, date, or time type
                    if field_type in ["DateTimeField", "DateField", "TimeField"]:
                        try:
                            value = parser.parse(value)
                            if field_type == "DateField":
                                value = value.date().strftime('%Y-%m-%d')
                            elif field_type == "TimeField":
                                value = value.time()
                            else:
                                value = value.strftime('%Y-%m-%d %H:%M:%S')
                            value = formats.localize(value)
                        except ValueError:
                            pass
                    # check if length is longer than 140 and truncate with ellipsis
                    if len(value) > 140:
                        value = "{}...".format(value[:140])

                    values_display.append(value)
            verbose_name = model_fields['mapping_fields'].get(field.name, field.verbose_name)
            changes_display_dict[verbose_name] = values_display
        return changes_display_dict


class AuditlogHistoryField(GenericRelation):
    """
    A subclass of py:class:`django.contrib.contenttypes.fields.GenericRelation` that sets some default variables. This
    makes it easier to access Auditlog's log entries, for example in templates.

    By default this field will assume that your primary keys are numeric, simply because this is the most common case.
    However, if you have a non-integer primary key, you can simply pass ``pk_indexable=False`` to the constructor, and
    Auditlog will fall back to using a non-indexed text based field for this model.

    Using this field will not automatically register the model for automatic logging. This is done so you can be more
    flexible with how you use this field.

    :param pk_indexable: Whether the primary key for this model is not an :py:class:`int` or :py:class:`long`.
    :type pk_indexable: bool
    """

    def __init__(self, pk_indexable=True, **kwargs):
        kwargs['to'] = LogEntry

        if pk_indexable:
            kwargs['object_id_field'] = 'object_id'
        else:
            kwargs['object_id_field'] = 'object_pk'

        kwargs['content_type_field'] = 'content_type'
        super(AuditlogHistoryField, self).__init__(**kwargs)

# South compatibility for AuditlogHistoryField
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^auditlog\.models\.AuditlogHistoryField"])
    #raise DeprecationWarning("South support will be dropped in django-auditlog 0.4.0 or later.")
except ImportError:
    pass
