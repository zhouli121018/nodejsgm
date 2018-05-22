# coding=utf-8
from ajax_select import register,LookupChannel
from apps.core.models import Customer
from django.db.models import Q
from django.utils.six import text_type
from django.utils.html import escape

@register('customer')
class CustomerLookup(LookupChannel):

    model = Customer

    def get_query(self, q, request):
        return Customer.objects.filter(Q(username__icontains=q) | Q(company__icontains=q)).order_by('username')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return text_type(obj)

    def get_objects(self, ids):
        return Customer.objects.filter(pk__in=ids)

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        return u"<span>%s(%s)</span>" % (escape(obj.company), escape(obj.username))