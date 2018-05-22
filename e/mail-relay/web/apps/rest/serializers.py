# coding=utf-8
import datetime
import time
import string
import threading
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.transaction import atomic
from django.db.models.signals import pre_save
from django.utils.functional import curry
from django.apps import apps
from auditlog.models import LogEntry
from apps.core.common import allocate_ippool_for_customer

from apps.core.models import Customer, CustomerIp, CustomerDomain, CustomerMailbox, ColCustomerDomain
from apps.mail.models import SubjectKeywordBlacklist, SenderBlacklist, KeywordBlacklist, AttachmentTypeBlacklist, \
    CheckSettings, AttachmentBlacklist, Settings
from apps.flag.models import SpamFlag
from auditlog.middleware import AuditlogMiddleware

threadlocal = threading.local()


# Serializers define the API representation.
class CustomerSerializer(serializers.ModelSerializer):
    ip = serializers.StringRelatedField(many=True)
    domain = serializers.StringRelatedField(many=True)
    mailbox = serializers.StringRelatedField(many=True)
    col_domain = serializers.StringRelatedField(many=True)
    tech_name = serializers.CharField(required=False)
    sale_name = serializers.CharField(required=False)
    service_name = serializers.CharField(required=False)

    class Meta:
        model = Customer
        fields = (
            'id', 'username', 'company', 'service_start', 'service_end', 'ip', 'domain', 'mailbox', 'col_domain',
            'status', 'created', 'support_id', 'support_name', 'support_email', 'email', 'mobile', 'contact',
            'relay_limit', 'collect_limit', 'gateway_service_start', 'gateway_service_end', 'gateway_status', 'tech_name', 'sale_name', 'service_name', 'is_webmail')

    def _get_setting(self):
        class DefaultSetting(object):
            expired_days = 15

        setting = DefaultSetting
        settings = Settings.objects.all()
        if settings:
            setting = settings[0]
        return setting

    def _update_status(self, instance):
        setting = self._get_setting()
        today = datetime.date.today()
        # 根据中继服务时间　判断中继客户状态
        if instance.service_end:
            if instance.service_end <= today:
                if (instance.service_end + datetime.timedelta(
                        days=setting.expired_days) >= today) and instance.company.find(u'临时信任') == -1:
                    if instance.status != 'expired':
                        instance.status = 'expired'
                else:
                    if instance.status != 'disabled':
                        instance.status = 'disabled'
            else:
                if instance.service_end - datetime.timedelta(days=10) <= today:
                    if instance.status != 'expiring':
                        instance.status = 'expiring'
                else:
                    if instance.status != 'normal':
                        instance.status = 'normal'
        else:
            instance.status = 'disabled'
        # 根据网关服务时间　判断网关客户状态
        if instance.gateway_service_end:
            if instance.gateway_service_end <= today:
                if (instance.gateway_service_end + datetime.timedelta(
                        days=setting.expired_days) >= today) and instance.company.find(u'临时信任') == -1:
                    if instance.gateway_status != 'expired':
                        instance.gateway_status = 'expired'
                else:
                    if instance.gateway_status != 'disabled':
                        instance.gateway_status = 'disabled'
            else:
                if instance.gateway_service_end - datetime.timedelta(days=10) <= today:
                    if instance.gateway_status != 'expiring':
                        instance.gateway_status = 'expiring'
                else:
                    if instance.gateway_status != 'normal':
                        instance.gateway_status = 'normal'
        else:
            instance.gateway_status = 'disabled'

        instance.save()


    def create(self, validated_data):
        service_start = validated_data['service_start']
        service_end = validated_data['service_end']
        created = validated_data['created']
        status = validated_data['status']
        relay_limit = validated_data['relay_limit']
        collect_limit = validated_data['collect_limit']
        gateway_service_start = validated_data['gateway_service_start']
        gateway_service_end = validated_data['gateway_service_end']
        gateway_status = validated_data['gateway_status']
        is_webmail = validated_data['is_webmail']
        if status == '':
            status = 'normal'
        if gateway_status == '':
            gateway_status = 'normal'
        if relay_limit == '':
            relay_limit = 0
        if collect_limit == '':
            collect_limit = 0
        if is_webmail == '':
            is_webmail = 0

        """
        if not service_start:
            service_start = str(datetime.date.today())
        service_start = datetime.datetime.strptime(service_start, '%Y-%m-%d').date()

        if not service_end:
            service_end = str(service_start + datetime.timedelta(days=30))
        service_end = datetime.datetime.strptime(service_end, '%Y-%m-%d').date()

        if not gateway_service_start:
            gateway_service_start = str(datetime.date.today())
        gateway_service_start = datetime.datetime.strptime(gateway_service_start, '%Y-%m-%d').date()

        if not gateway_service_end:
            gateway_service_end = str(gateway_service_start + datetime.timedelta(days=30))
        gateway_service_end = datetime.datetime.strptime(gateway_service_end, '%Y-%m-%d').date()
        """

        try:
            created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
        except BaseException, e:
            created = datetime.datetime.now()

        if Customer.objects.filter(username=validated_data['username']):
            raise serializers.ValidationError(u'username不能重复')
        if Customer.objects.filter(company=validated_data['company']):
            raise serializers.ValidationError(u'company不能重复')
        if Customer.objects.filter(support_id=validated_data['support_id']):
            raise serializers.ValidationError(u'support_id不能重复')

        customer = Customer(
            id=validated_data['id'],
            username=validated_data['username'],
            company=validated_data['company'],
            support_id=validated_data['support_id'],
            support_name=validated_data['support_name'],
            support_email=validated_data['support_email'],
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            contact=validated_data['contact'],
            # service_start=service_start,
            # service_end=service_end,
            status=status,
            created=created,
            relay_limit=relay_limit,
            is_webmail=is_webmail,
            collect_limit=collect_limit,
            # gateway_service_start=gateway_service_start,
            # gateway_service_end=gateway_service_end,
            gateway_status=gateway_status,
        )
        if service_start:
            customer.service_start = datetime.datetime.strptime(service_start,
                                                                '%Y-%m-%d').date() if service_start != '-1' else None
        if service_end:
            customer.service_end = datetime.datetime.strptime(service_end,
                                                              '%Y-%m-%d').date() if service_end != '-1' else None
        if gateway_service_start:
            customer.gateway_service_start = datetime.datetime.strptime(gateway_service_start,
                                                                        '%Y-%m-%d').date() if gateway_service_start != '-1' else None
        if gateway_service_end:
            customer.gateway_service_end = datetime.datetime.strptime(gateway_service_end,
                                                                      '%Y-%m-%d').date() if gateway_service_end != '-1' else None
        if validated_data['tech']:
            customer.tech = validated_data['tech']

        if validated_data['sale']:
            customer.sale = validated_data['sale']

        if validated_data['service']:
            customer.service = validated_data['service']

        if validated_data['operater']:
            customer.creater = validated_data['operater']


        self._update_status(customer)

        allocate_ippool_for_customer(customer.id)
        disabled = True if status == 'disabled' else False

        for i in validated_data['ip']:
            CustomerIp.objects.create(ip=i, customer=customer, disabled=disabled)

        for d in validated_data['domain']:
            CustomerDomain.objects.create(domain=d, customer=customer, disabled=disabled)

        for d in validated_data['col_domain']:
            domain, forward_address = d.split('----', 1)
            forward_address = forward_address.strip()
            if not domain or not forward_address:
                continue
            ColCustomerDomain.objects.create(domain=domain, forward_address=forward_address, customer=customer,
                                             disabled=disabled)

        for m in validated_data['mailbox']:
            mailbox, password = m.split('----', 1)
            if not mailbox or not password:
                continue
            CustomerMailbox.objects.create(mailbox=mailbox, password=password, customer=customer, disabled=disabled)
        return customer

    def update(self, instance, validated_data):

        if validated_data['username']:
            instance.username = validated_data['username']

        if validated_data['company']:
            instance.company = validated_data['company']

        if validated_data['relay_limit'] != '':
            instance.relay_limit = validated_data['relay_limit']

        if validated_data['is_webmail'] != '':
            instance.is_webmail = validated_data['is_webmail']

        if validated_data['collect_limit'] != '':
            instance.collect_limit = validated_data['collect_limit']

        if validated_data['support_id']:
            instance.support_id = validated_data['support_id']

        if validated_data['support_name']:
            instance.support_name = validated_data['support_name']
        if validated_data['support_email']:
            instance.support_email = validated_data['support_email']

        if validated_data['email']:
            instance.email = validated_data['email']
        if validated_data['mobile']:
            instance.mobile = validated_data['mobile']
        if validated_data['contact']:
            instance.contact = validated_data['contact']

        if validated_data['service_start']:
            instance.service_start = datetime.datetime.strptime(validated_data['service_start'], '%Y-%m-%d').date() if \
                validated_data['service_start'] != '-1' else None

        if validated_data['service_end']:
            instance.service_end = datetime.datetime.strptime(validated_data['service_end'], '%Y-%m-%d').date() if \
                validated_data['service_end'] != '-1' else None

        if validated_data['status']:
            instance.status = validated_data['status']

        if validated_data['gateway_service_start']:
            instance.gateway_service_start = datetime.datetime.strptime(validated_data['gateway_service_start'],
                                                                        '%Y-%m-%d').date() if validated_data[
                                                                                                  'gateway_service_start'] != '-1' else None

        if validated_data['gateway_service_end']:
            instance.gateway_service_end = datetime.datetime.strptime(validated_data['gateway_service_end'],
                                                                      '%Y-%m-%d').date() if validated_data[
                                                                                                'gateway_service_end'] != '-1' else None

        if validated_data['gateway_status']:
            instance.gateway_status = validated_data['gateway_status']

        if validated_data['created']:
            try:
                created = datetime.datetime.strptime(validated_data['created'], '%Y-%m-%d %H:%M:%S')
            except BaseException, e:
                created = datetime.datetime.now()
            instance.created = created

        if validated_data['tech']:
            instance.tech = validated_data['tech']

        if validated_data['sale']:
            instance.sale = validated_data['sale']

        if validated_data['operater']:
            instance.operater = validated_data['operater']

        if validated_data['service']:
            instance.service = validated_data['service']
        self._update_status(instance)

        for i in validated_data['ip']:
            obj, rs = CustomerIp.objects.get_or_create(customer=instance, ip=i)
            if not rs:
                obj.disabled = False
                obj.save()

        for d in validated_data['domain']:
            obj, rs = CustomerDomain.objects.get_or_create(customer=instance, domain=d)
            if not rs:
                obj.disabled = False
                obj.save()

        for d in validated_data['col_domain']:
            domain, forward_address = d.split('----', 1)
            forward_address = forward_address.strip()
            obj, rs = ColCustomerDomain.objects.get_or_create(customer=instance, domain=domain,
                                                              forward_address=forward_address)
            if not rs:
                obj.disabled = False
                obj.save()

        for m in validated_data['mailbox']:
            mailbox, password = m.split('----', 1)
            objs = CustomerMailbox.objects.filter(customer=instance, mailbox=mailbox)
            if objs:
                objs.update(password=password, disabled=False)
            else:
                CustomerMailbox.objects.create(mailbox=mailbox, password=password, customer=instance)

        for i in validated_data['delete_ip']:
            CustomerIp.objects.filter(customer=instance, ip=i).delete()

        for d in validated_data['delete_domain']:
            CustomerDomain.objects.filter(customer=instance, domain=d).delete()

        for m in validated_data['delete_mailbox']:
            mailbox = m.split('----', 1)[0]
            CustomerMailbox.objects.filter(customer=instance, mailbox=mailbox).delete()

        for d in validated_data['delete_col_domain']:
            domain, forward_address = d.split('----', 1)
            forward_address = forward_address.strip()
            ColCustomerDomain.objects.filter(customer=instance, domain=domain, forward_address=forward_address).delete()

        for i in validated_data['disabled_ip']:
            CustomerIp.objects.filter(customer=instance, ip=i).update(disabled=True)

        for d in validated_data['disabled_domain']:
            CustomerDomain.objects.filter(customer=instance, domain=d).update(disabled=True)

        for d in validated_data['disabled_col_domain']:
            domain, forward_address = d.split('----', 1)
            forward_address = forward_address.strip()
            ColCustomerDomain.objects.filter(customer=instance, domain=domain, forward_address=forward_address).update(
                disabled=True)

        for m in validated_data['disabled_mailbox']:
            mailbox = m.split('----', 1)[0]
            CustomerMailbox.objects.filter(customer=instance, mailbox=mailbox).update(disabled=True)
        return instance

    def to_internal_value(self, data):
        data['id'] = data.get('id', None)
        data['username'] = data.get('username', '').strip()
        data['company'] = data.get('company', '').strip()
        data['support_id'] = data.get('support_id', '').strip()
        data['support_name'] = data.get('support_name', '').strip()
        data['support_email'] = data.get('support_email', '').strip()
        data['email'] = data.get('email', '').strip()
        data['mobile'] = data.get('mobile', '').strip()
        data['contact'] = data.get('contact', '').strip()
        data['service_start'] = data.get('service_start', '')
        data['service_end'] = data.get('service_end', '')
        data['status'] = data.get('status', '').strip()
        data['created'] = data.get('created', '').strip()
        data['gateway_service_start'] = data.get('gateway_service_start', '')
        data['gateway_service_end'] = data.get('gateway_service_end', '')
        data['gateway_status'] = data.get('gateway_status', '').strip()
        try:
            data['is_webmail'] = int(data.get('is_webmail', '').strip())
        except:
            data['is_webmail'] = ''
        try:
            data['operater'] = User.objects.get(username=data.get('operater', '').strip())
        except:
            data['operater'] = ''

        # 记录操作日志　auditlog
        if data['operater']:
            threadlocal.auditlog = {
                'signal_duid': (self.__class__, time.time()),
            }
            set_actor = curry(AuditlogMiddleware.set_actor, user=data['operater'], signal_duid=None)
            pre_save.connect(set_actor, sender=LogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'], weak=False)

        try:
            data['relay_limit'] = int(data.get('relay_limit', '').strip())
        except:
            data['relay_limit'] = ''
        try:
            data['collect_limit'] = int(data.get('collect_limit', '').strip())
        except:
            data['collect_limit'] = ''

        data['ip'] = filter(lambda d: d, map(string.strip, data.get('ip', '').split(',')))
        data['domain'] = filter(lambda d: d, map(string.strip, data.get('domain', '').split(',')))
        data['col_domain'] = filter(lambda d: d, map(string.strip, data.get('col_domain', '').split(',')))
        data['mailbox'] = filter(lambda d: d, map(string.strip, data.get('mailbox', '').split(',')))

        data['delete_ip'] = filter(lambda d: d, map(string.strip, data.get('delete_ip', '').split(',')))
        data['delete_domain'] = filter(lambda d: d, map(string.strip, data.get('delete_domain', '').split(',')))
        data['delete_mailbox'] = filter(lambda d: d, map(string.strip, data.get('delete_mailbox', '').split(',')))
        data['delete_col_domain'] = filter(lambda d: d, map(string.strip, data.get('delete_col_domain', '').split(',')))

        data['disabled_ip'] = filter(lambda d: d, map(string.strip, data.get('disabled_ip', '').split(',')))
        data['disabled_domain'] = filter(lambda d: d, map(string.strip, data.get('disabled_domain', '').split(',')))
        data['disabled_mailbox'] = filter(lambda d: d, map(string.strip, data.get('disabled_mailbox', '').split(',')))
        data['disabled_col_domain'] = filter(lambda d: d,
                                             map(string.strip, data.get('disabled_col_domain', '').split(',')))

        try:
            data['tech'] = User.objects.get(username=data.get('tech_name', ''))
        except:
            data['tech'] = ''
        try:
            data['sale'] = User.objects.get(username=data.get('sale_name', ''))
        except:
            data['sale'] = ''
        try:
            data['service'] = User.objects.get(username=data.get('service_name', ''))
        except:
            data['service'] = ''
        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password_md5 = serializers.CharField(style={'input_type': 'password'}, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password_md5', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_active')


    def to_internal_value(self, data):
        password = data.get('password_md5')
        is_active = data.get('is_active', '')
        data['is_active'] = False if is_active.lower() == 'f' else True
        if not password:
            password = data.get('password')
            if password:
                password = make_password(password)
        if password:
            data['password'] = password
        return data


class SubjectKeywordBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectKeywordBlacklist
        fields = ('keyword', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'is_regex')


class KeywordBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordBlacklist
        fields = ('keyword', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'is_regex')


class SenderBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SenderBlacklist
        fields = ('keyword', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'is_regex')


class AttachmentBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentBlacklist
        fields = ('keyword', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'is_regex')


class AttachmentTypeBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentTypeBlacklist
        fields = ('keyword', )


class CheckSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckSettings
        fields = ('c_spam_score_max', 'c_night_spam_score_max', 'spam_score_max', 'night_spam_score_max', 'subject_max_size', 'content_max_size', 'sender_max_size',
                  'spam_max_size', 'dspam_max_size', 'ctasd_max_size', 'attachment_min_size',
                  'collect_attachment_min_size')


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'company', 'support_id')


class SpamFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamFlag
        fields = ('keyword', )
