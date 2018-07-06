
from django.forms.widgets import Input, Select
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class DatalistTextInput(Input, Select):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self.format_value(value))
        name_list = "{}_list".format(name)
        name_error = "{}_error".format(name)
        output = [format_html('<input list="{}" {} />', name_list, flatatt(final_attrs))]
        options = self.render_options(value)
        if options:
            output.append('<datalist id="{}">'.format(name_list))
            output.append(options)
            output.append('</datalist>')
        output.append('<span style="color:#b94a48;" id="{}"></span>'.format(name_error))
        return mark_safe('\n'.join(output))