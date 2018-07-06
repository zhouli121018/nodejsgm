# coding=utf-8
from django import template
from django.conf import settings
from app.core.models import CustomerMailbox, CustomerDomain, CustomerDomainMailboxRel
register = template.Library()

@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.filter
def get_mailbox_count(domain, customer):
    return CustomerMailbox.objects.filter(customer=customer, domain=domain).count()

@register.filter
def get_share_mailbox_count(domain_id, customer):
    domain_obj = CustomerDomain.objects.get(id=domain_id, customer=customer.parent)
    domain = domain_obj.domain
    ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
    box_ids = CustomerDomainMailboxRel.objects.filter(customer=customer, content_type=ctype).values_list('object_id', flat=True)
    return CustomerMailbox.objects.filter(customer=customer.parent, domain=domain, id__in=box_ids).count()
