from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework import filters
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from .rest_mixins import RestModelViewSet

from apps.core.models import Customer
from serializers import CustomerSerializer, UserSerializer, SubjectKeywordBlacklistSerializer, \
    KeywordBlacklistSerializer, SenderBlacklistSerializer, AttachmentTypeBlacklistSerializer, \
    AttachmentBlacklistSerializer, CheckSettingsSerializer, SupportSerializer, SpamFlagSerializer
from apps.mail.models import SubjectKeywordBlacklist, KeywordBlacklist, SenderBlacklist, AttachmentTypeBlacklist, AttachmentBlacklist, CheckSettings
from apps.flag.models import SpamFlag



# ViewSets define the view behavior.
class CustomerViewSet(RestModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username', 'company', 'support_id')


class UserViewSet(RestModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username', 'first_name')

class SupportViewSet(RestModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = SupportSerializer

class SubjectKeywordBlacklistViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    queryset = SubjectKeywordBlacklist.objects.exclude(collect=False, relay=False)
    serializer_class = SubjectKeywordBlacklistSerializer


class KeywordBlacklistViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    queryset = KeywordBlacklist.objects.exclude(collect=False, relay=False)
    serializer_class = KeywordBlacklistSerializer


class SenderBlacklistViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    queryset = SenderBlacklist.objects.exclude(collect=False, relay=False)
    serializer_class = SenderBlacklistSerializer

class AttachmentBlacklistViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    queryset = AttachmentBlacklist.objects.exclude(collect=False, relay=False)
    serializer_class = AttachmentBlacklistSerializer


class AttachmentTypeBlacklistViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    queryset = AttachmentTypeBlacklist.objects.filter(disabled=False)
    serializer_class = AttachmentTypeBlacklistSerializer


class CheckSettingsViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    queryset = CheckSettings.objects.all()
    serializer_class = CheckSettingsSerializer

class SpamFlagViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    queryset = SpamFlag.objects.all()
    serializer_class = SpamFlagSerializer
