from django.contrib import admin
from ajax_select import make_ajax_form
from models import SenderWhitelist
from ajax_select.admin import AjaxSelectAdmin

class SenderWhitelistAdmin(AjaxSelectAdmin):

    form = make_ajax_form(SenderWhitelist,{'customer':'customer'})
    
admin.site.register(SenderWhitelist, SenderWhitelistAdmin)

# Register your models here.
