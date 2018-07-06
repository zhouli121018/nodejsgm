# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import Field, CallableChoiceIterator, ChoiceField
from app.trigger.utils.widgets import DatalistTextInput


class CustomerChoiceField(ChoiceField):
    ''' 继承 ChoiceField 去掉验证
    '''
    def validate(self, value):
        pass

class DatalistCharField(Field):
    widget = DatalistTextInput
    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the available choices.'),
    }

    def __init__(self, max_length=None, min_length=None, strip=True,
                 choices=(), required=True, widget=None, label=None,
                 initial=None, help_text='', *args, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        self.strip = strip
        super(DatalistCharField, self).__init__(
            required=required, widget=widget, label=label, initial=initial,
            help_text=help_text, *args, **kwargs
        )
        self.choices = choices

    def __deepcopy__(self, memo):
        result = super(DatalistCharField, self).__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        if callable(value):
            value = CallableChoiceIterator(value)
        else:
            value = list(value)

        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)

    def to_python(self, value):
        "Returns a Unicode object."
        if value in self.empty_values:
            return ''
        value = force_text(value)
        if self.strip:
            value = value.strip()
        return value

    def widget_attrs(self, widget):
        attrs = super(DatalistCharField, self).widget_attrs(widget)
        if self.max_length is not None:
            # The HTML attribute is maxlength, not max_length.
            attrs['maxlength'] = str(self.max_length)
        if self.min_length is not None:
            # The HTML attribute is minlength, not min_length.
            attrs['minlength'] = str(self.min_length)
        return attrs