from django.conf.urls import patterns, url, include
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from views import CustomerViewSet, UserViewSet, SubjectKeywordBlacklistViewSet, KeywordBlacklistViewSet, \
    SenderBlacklistViewSet, AttachmentTypeBlacklistViewSet, AttachmentBlacklistViewSet, CheckSettingsViewSet, \
    SupportViewSet, SpamFlagViewSet
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'users', UserViewSet)
router.register(r'subject_blacklist', SubjectKeywordBlacklistViewSet)
router.register(r'keyword_blacklist', KeywordBlacklistViewSet)
router.register(r'sender_blacklist', SenderBlacklistViewSet)
router.register(r'attach_type_blacklist', AttachmentTypeBlacklistViewSet)
router.register(r'attach_blacklist', AttachmentBlacklistViewSet)
router.register(r'setting_blacklist', CheckSettingsViewSet)
router.register(r'supports', SupportViewSet)
router.register(r'spam_flag', SpamFlagViewSet)

urlpatterns = patterns('',
   url(r'^$', login_required(router.get_api_root_view()), name=router.root_view_name),
   url(r'', include(router.urls))
)
