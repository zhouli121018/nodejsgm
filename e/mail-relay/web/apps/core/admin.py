from django.contrib import admin
from apps.core.models import Customer


# Register your models here.

from ordered_model.admin import OrderedModelAdmin
class CustomerAdmin(OrderedModelAdmin):
    list_display = ('username', 'move_up_down_links')

admin.site.register(Customer, CustomerAdmin)
