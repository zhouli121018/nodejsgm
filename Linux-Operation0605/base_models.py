# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Admin(models.Model):
    domain_id = models.IntegerField()
    username = models.CharField(max_length=40, blank=True, null=True)
    password = models.CharField(max_length=120, blank=True, null=True)
    usertype = models.CharField(max_length=11)
    lastlogin = models.DateTimeField()
    lastip = models.CharField(max_length=20, blank=True, null=True)
    disabled = models.CharField(max_length=2)
    ip_limit = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.IntegerField()
    is_staff = models.IntegerField()
    is_superuser = models.IntegerField()
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'admin'


class AdminLog(models.Model):
    operator = models.CharField(max_length=15, blank=True, null=True)
    classify = models.CharField(max_length=15, blank=True, null=True)
    datetime = models.DateTimeField()
    object = models.CharField(max_length=15, blank=True, null=True)
    action = models.CharField(max_length=35, blank=True, null=True)
    result = models.CharField(max_length=2)
    description = models.CharField(max_length=100, blank=True, null=True)
    clientip = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_log'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class AuthUserGroups(models.Model):
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class CoCompany(models.Model):
    domain_id = models.IntegerField(unique=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    homepage = models.CharField(max_length=100, blank=True, null=True)
    addr_country = models.CharField(max_length=50, blank=True, null=True)
    addr_state = models.CharField(max_length=50, blank=True, null=True)
    addr_city = models.CharField(max_length=50, blank=True, null=True)
    addr_address = models.CharField(max_length=100, blank=True, null=True)
    addr_zip = models.CharField(max_length=20, blank=True, null=True)
    telphone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'co_company'


class CoDepartment(models.Model):
    domain_id = models.IntegerField()
    parent_id = models.IntegerField()
    title = models.CharField(max_length=100, blank=True, null=True)
    showorder = models.IntegerField()
    modlimit = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'co_department'


class CoDepartmentInfo(models.Model):
    dept_id = models.IntegerField(unique=True)
    domain_id = models.IntegerField()
    manager = models.CharField(max_length=50, blank=True, null=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    telphone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=80, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'co_department_info'


class CoDepartmentMember(models.Model):
    domain_id = models.IntegerField()
    dept_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    position = models.CharField(max_length=35, blank=True, null=True)
    is_admin = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'co_department_member'
        unique_together = (('dept_id', 'mailbox_id'),)


class CoGroup(models.Model):
    domain_id = models.IntegerField()
    title = models.CharField(max_length=100, blank=True, null=True)
    desp = models.TextField()
    check_level = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'co_group'


class CoGroupMember(models.Model):
    domain_id = models.IntegerField()
    group_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    position = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'co_group_member'


class CoUser(models.Model):
    mailbox_id = models.IntegerField(primary_key=True)
    domain_id = models.IntegerField()
    realname = models.CharField(max_length=35, blank=True, null=True)
    engname = models.CharField(max_length=35, blank=True, null=True)
    oabshow = models.CharField(max_length=2)
    showorder = models.IntegerField()
    eenumber = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=6)
    birthday = models.DateField()
    homepage = models.CharField(max_length=100, blank=True, null=True)
    tel_mobile = models.CharField(max_length=20, blank=True, null=True)
    tel_home = models.CharField(max_length=20, blank=True, null=True)
    tel_work = models.CharField(max_length=20, blank=True, null=True)
    tel_work_ext = models.CharField(max_length=10, blank=True, null=True)
    tel_group = models.CharField(max_length=20, blank=True, null=True)
    im_qq = models.CharField(max_length=25, blank=True, null=True)
    im_msn = models.CharField(max_length=50, blank=True, null=True)
    addr_country = models.CharField(max_length=50, blank=True, null=True)
    addr_state = models.CharField(max_length=50, blank=True, null=True)
    addr_city = models.CharField(max_length=50, blank=True, null=True)
    addr_address = models.CharField(max_length=100, blank=True, null=True)
    addr_zip = models.CharField(max_length=20, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    last_session = models.CharField(max_length=32, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    openid = models.CharField(max_length=128)
    unionid = models.CharField(max_length=255)
    wx_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'co_user'


class CoUserAttr(models.Model):
    mailbox_id = models.IntegerField()
    domain_id = models.IntegerField()
    type = models.CharField(max_length=6)
    item = models.CharField(max_length=35, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'co_user_attr'
        unique_together = (('mailbox_id', 'type', 'item'),)


class CoUserCancel(models.Model):
    domain_id = models.IntegerField(blank=True, null=True)
    mailbox_id = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    remark = models.TextField()
    status = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'co_user_cancel'


class CoUserChange(models.Model):
    domain_id = models.IntegerField(blank=True, null=True)
    mailbox_id = models.IntegerField()
    realname = models.CharField(max_length=35, blank=True, null=True)
    engname = models.CharField(max_length=35, blank=True, null=True)
    eenumber = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField()
    homepage = models.CharField(max_length=100, blank=True, null=True)
    tel_mobile = models.CharField(max_length=20, blank=True, null=True)
    tel_home = models.CharField(max_length=20, blank=True, null=True)
    tel_work = models.CharField(max_length=20, blank=True, null=True)
    tel_work_ext = models.CharField(max_length=10, blank=True, null=True)
    tel_group = models.CharField(max_length=20, blank=True, null=True)
    im_qq = models.CharField(max_length=25, blank=True, null=True)
    im_msn = models.CharField(max_length=50, blank=True, null=True)
    addr_country = models.CharField(max_length=50, blank=True, null=True)
    addr_state = models.CharField(max_length=50, blank=True, null=True)
    addr_city = models.CharField(max_length=50, blank=True, null=True)
    addr_address = models.CharField(max_length=100, blank=True, null=True)
    addr_zip = models.CharField(max_length=20, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    change_content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=6)
    created = models.DateTimeField(blank=True, null=True)
    gender = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'co_user_change'


class CoUserLog(models.Model):
    domain_id = models.IntegerField(blank=True, null=True)
    mailbox_id = models.IntegerField(blank=True, null=True)
    reg_id = models.IntegerField(blank=True, null=True)
    classify = models.CharField(max_length=64, blank=True, null=True)
    datetime = models.DateTimeField()
    action = models.CharField(max_length=35, blank=True, null=True)
    result = models.CharField(max_length=2)
    description = models.CharField(max_length=2000, blank=True, null=True)
    clientip = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'co_user_log'


class CoUserReg(models.Model):
    domain_id = models.IntegerField()
    username = models.CharField(max_length=35, blank=True, null=True)
    password = models.CharField(max_length=40, blank=True, null=True)
    realname = models.CharField(max_length=35, blank=True, null=True)
    engname = models.CharField(max_length=35, blank=True, null=True)
    eenumber = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    department = models.IntegerField()
    remark = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=6)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'co_user_reg'


class CoUserVisitlog(models.Model):
    sessionid = models.CharField(max_length=64, blank=True, null=True)
    domain_id = models.IntegerField(blank=True, null=True)
    mailbox_id = models.IntegerField(blank=True, null=True)
    logintime = models.DateTimeField(blank=True, null=True)
    lasttime = models.DateTimeField(blank=True, null=True)
    clienttype = models.CharField(max_length=32, blank=True, null=True)
    clientip = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'co_user_visitlog'


class CoreAlias(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    type = models.CharField(max_length=7)
    source = models.CharField(max_length=200, blank=True, null=True)
    target = models.TextField(blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'core_alias'


class CoreAuthLog(models.Model):
    domain_id = models.IntegerField(blank=True, null=True)
    user = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    client_ip = models.CharField(max_length=20, blank=True, null=True)
    is_login = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=1000, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_auth_log'


class CoreAuthLogHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    domain_id = models.IntegerField(blank=True, null=True)
    user = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    client_ip = models.CharField(max_length=20, blank=True, null=True)
    is_login = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_auth_log_history'


class CoreBcc(models.Model):
    domain_id = models.IntegerField()
    target = models.CharField(max_length=80, blank=True, null=True)
    target_dept = models.IntegerField()
    forward = models.CharField(max_length=80, blank=True, null=True)
    type = models.CharField(max_length=9)
    disabled = models.CharField(max_length=2)
    target_type = models.CharField(max_length=20)
    monit_move = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'core_bcc'


class CoreBlacklist(models.Model):
    operator = models.CharField(max_length=4)
    type = models.CharField(max_length=4)
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    email = models.CharField(max_length=60, blank=True, null=True)
    disabled = models.CharField(max_length=2)
    add_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_blacklist'


class CoreConfig(models.Model):
    function = models.CharField(max_length=50, blank=True, null=True)
    enabled = models.CharField(max_length=2)
    param = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_config'


class CoreDomain(models.Model):
    domain_id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=50, blank=True, null=True)
    antivirus = models.CharField(max_length=2)
    antispam = models.CharField(max_length=2)
    sendlimit = models.CharField(max_length=2)
    dkim = models.CharField(max_length=2)
    recvsms = models.CharField(max_length=2)
    sendsms = models.CharField(max_length=2)
    userbwlist = models.CharField(max_length=2)
    popmail = models.CharField(max_length=2)
    spaceclean = models.CharField(max_length=2)
    impush = models.CharField(max_length=2)
    disabled = models.CharField(max_length=2)
    share_domains = models.CharField(max_length=200)
    share_title = models.CharField(max_length=200)
    is_wx_host = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_domain'


class CoreDomainAttr(models.Model):
    domain_id = models.IntegerField()
    type = models.CharField(max_length=7, blank=True, null=True)
    item = models.CharField(max_length=35, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_domain_attr'
        unique_together = (('domain_id', 'type', 'item'),)


class CoreDomainLoginTemp(models.Model):
    temp_id = models.AutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=80)
    temp_name = models.CharField(max_length=200)
    add_time = models.IntegerField(blank=True, null=True)
    update_time = models.IntegerField(blank=True, null=True)
    folder = models.CharField(max_length=200)
    src = models.CharField(max_length=100)
    type = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_domain_login_temp'
        unique_together = (('folder', 'type'),)


class CoreInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    superadmintitle = models.CharField(max_length=250)
    systemadmintitle = models.CharField(max_length=250)
    domainadmintitle = models.CharField(max_length=250)
    deptadmintitle = models.CharField(max_length=250)
    domain_main = models.CharField(max_length=200)
    domain_attr = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'core_info'


class CoreMailList(models.Model):
    add_time = models.IntegerField()
    pwd = models.CharField(max_length=40)
    uid = models.IntegerField()
    msgno = models.IntegerField()
    folder = models.CharField(max_length=200)
    status = models.IntegerField()
    subject = models.CharField(max_length=500)
    toaddress = models.CharField(max_length=1000)
    fromaddress = models.CharField(max_length=1000)
    maildate = models.IntegerField()
    pwd_status = models.IntegerField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'core_mail_list'


class CoreMailLog(models.Model):
    main_id = models.CharField(max_length=30, blank=True, null=True)
    domain_id = models.IntegerField(blank=True, null=True)
    mailbox_id = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=10)
    send_mail = models.CharField(max_length=100, blank=True, null=True)
    rcv_mail = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    size = models.BigIntegerField(blank=True, null=True)
    attachment = models.CharField(max_length=3000, blank=True, null=True)
    attachment_size = models.BigIntegerField(blank=True, null=True)
    result = models.CharField(max_length=2)
    description = models.TextField(blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    recv_time = models.DateTimeField(blank=True, null=True)
    senderip = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    rcv_server = models.CharField(max_length=100, blank=True, null=True)
    folder = models.CharField(max_length=100, blank=True, null=True)
    remark = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_mail_log'


class CoreMailLogHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    main_id = models.CharField(max_length=30, blank=True, null=True)
    domain_id = models.IntegerField(blank=True, null=True)
    mailbox_id = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    send_mail = models.CharField(max_length=100, blank=True, null=True)
    rcv_mail = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    size = models.BigIntegerField(blank=True, null=True)
    attachment = models.CharField(max_length=3000, blank=True, null=True)
    attachment_size = models.BigIntegerField(blank=True, null=True)
    result = models.CharField(max_length=2)
    description = models.TextField(blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    recv_time = models.DateTimeField(blank=True, null=True)
    senderip = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    rcv_server = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_mail_log_history'


class CoreMailLogdate(models.Model):
    logdate = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_mail_logdate'


class CoreMailbox(models.Model):
    mailbox_id = models.AutoField(primary_key=True)
    domain_id = models.IntegerField()
    domain = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=80)
    mailbox = models.CharField(unique=True, max_length=200)
    password = models.CharField(max_length=120, blank=True, null=True)
    savepath = models.CharField(max_length=100, blank=True, null=True)
    quota_mailbox = models.IntegerField()
    quota_netdisk = models.IntegerField()
    limit_send = models.CharField(max_length=2)
    limit_recv = models.CharField(max_length=2)
    limit_pop = models.CharField(max_length=2)
    limit_imap = models.CharField(max_length=2)
    limit_login = models.CharField(max_length=2)
    recvsms = models.CharField(max_length=2)
    sys_mailbox = models.CharField(max_length=2)
    disabled = models.CharField(max_length=2)
    ip_limit = models.CharField(max_length=255, blank=True, null=True)
    change_pwd = models.CharField(max_length=2)
    enable_share = models.IntegerField()
    first_change_pwd = models.IntegerField(blank=True, null=True)
    pwd_days = models.IntegerField()
    pwd_days_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_mailbox'


class CoreNonce(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.CharField(unique=True, max_length=150)
    add_time = models.IntegerField()
    ip = models.CharField(max_length=30)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_nonce'


class CorePlan(models.Model):
    exec_time = models.IntegerField()
    interval_type = models.IntegerField()
    exec_interval = models.IntegerField()
    function_name = models.CharField(max_length=50)
    function_dec = models.CharField(max_length=200)
    is_enabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_plan'


class CorePlanLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    add_time = models.IntegerField()
    plan_id = models.IntegerField()
    status = models.IntegerField()
    function_name = models.CharField(max_length=50)
    ext = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'core_plan_log'


class CoreRelay(models.Model):
    domain_id = models.IntegerField()
    type = models.CharField(max_length=2)
    src_domain = models.CharField(max_length=80, blank=True, null=True)
    dst_domain = models.CharField(max_length=80, blank=True, null=True)
    server = models.CharField(max_length=80, blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'core_relay'


class CoreTrustip(models.Model):
    ip = models.CharField(max_length=48, blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'core_trustip'


class CoreUpgradeList(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    app = models.CharField(max_length=50, blank=True, null=True)
    prev_app = models.CharField(max_length=50, blank=True, null=True)
    webmail = models.CharField(max_length=50, blank=True, null=True)
    prev_webmail = models.CharField(max_length=50, blank=True, null=True)
    operation = models.CharField(max_length=50, blank=True, null=True)
    prev_operation = models.CharField(max_length=50, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_upgrade_list'


class CoreUpgradeLog(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    prev = models.CharField(max_length=50, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_upgrade_log'
        unique_together = (('name', 'version'),)


class CoreUrlRemark(models.Model):
    url = models.CharField(max_length=200)
    remark = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_url_remark'


class CoreWhitelist(models.Model):
    operator = models.CharField(max_length=4)
    type = models.CharField(max_length=4)
    version = models.IntegerField()
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    email = models.CharField(max_length=60, blank=True, null=True)
    disabled = models.CharField(max_length=2)
    add_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'core_whitelist'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class ExtAccountTransfer(models.Model):
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(max_length=200)
    mailbox_to = models.CharField(max_length=200)
    mode = models.CharField(max_length=200, blank=True, null=True)
    succ_del = models.IntegerField()
    status = models.CharField(max_length=20)
    last_update = models.DateTimeField()
    desc_msg = models.TextField(blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_account_transfer'
        unique_together = (('mailbox_id', 'mailbox_to'),)


class ExtAdsync(models.Model):
    domain_id = models.IntegerField()
    server_domain = models.CharField(max_length=100, blank=True, null=True)
    server = models.CharField(max_length=100, blank=True, null=True)
    port = models.IntegerField()
    account = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    ou = models.CharField(max_length=500, blank=True, null=True)
    create_acct = models.CharField(max_length=50)
    create_dept = models.CharField(max_length=50)
    remark = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_adsync'


class ExtCfilterCondition(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    rule_id = models.IntegerField()
    test_type = models.CharField(max_length=25, blank=True, null=True)
    test_logic = models.CharField(max_length=25, blank=True, null=True)
    test_param = models.CharField(max_length=255, blank=True, null=True)
    filter_target = models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'ext_cfilter_condition'


class ExtCfilterConditionList(models.Model):
    domain_id = models.IntegerField()
    type = models.IntegerField()
    condition = models.CharField(max_length=1000)
    sequence = models.IntegerField()
    rule_list = models.CharField(max_length=250, blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_cfilter_condition_list'


class ExtCfilterNewAction(models.Model):
    rule_id = models.IntegerField()
    action = models.CharField(max_length=50, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    sequence = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_cfilter_new_action'


class ExtCfilterNewCond(models.Model):
    parent_id = models.IntegerField()
    rule_id = models.IntegerField()
    logic = models.CharField(max_length=50)
    option = models.CharField(max_length=50)
    suboption = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_cfilter_new_cond'


class ExtCfilterNewLog(models.Model):
    task_id = models.CharField(max_length=50)
    subject = models.CharField(max_length=200, blank=True, null=True)
    sender = models.CharField(max_length=200, blank=True, null=True)
    recipient = models.TextField(blank=True, null=True)
    reason = models.CharField(max_length=50, blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    log_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_cfilter_new_log'


class ExtCfilterRule(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    system_rule = models.IntegerField()
    name = models.CharField(max_length=80, blank=True, null=True)
    condition_type = models.CharField(max_length=6)
    sequence = models.IntegerField()
    action_type = models.CharField(max_length=25, blank=True, null=True)
    action_param = models.TextField(blank=True, null=True)
    disabled = models.CharField(max_length=2)
    rule_type = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_cfilter_rule'


class ExtCfilterRuleNew(models.Model):
    mailbox_id = models.IntegerField()
    name = models.CharField(max_length=150, blank=True, null=True)
    type = models.IntegerField()
    logic = models.CharField(max_length=50)
    sequence = models.IntegerField()
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_cfilter_rule_new'


class ExtCheckruleCondition(models.Model):
    parent_id = models.IntegerField()
    logic = models.CharField(max_length=50)
    rule_id = models.IntegerField()
    option = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=20, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_checkrule_condition'


class ExtCollect(models.Model):
    address = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ext_collect'


class ExtCommonCheckrule(models.Model):
    mailbox_id = models.IntegerField()
    type = models.CharField(max_length=50, blank=True, null=True)
    logic = models.CharField(max_length=50, blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_common_checkrule'


class ExtEmailFlag(models.Model):
    mailbox_id = models.IntegerField()
    store_type = models.CharField(max_length=20)
    store_color = models.CharField(max_length=10)
    store_value = models.CharField(max_length=100, blank=True, null=True)
    message_id = models.CharField(max_length=200, blank=True, null=True)
    folder = models.CharField(max_length=200)
    imap_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_email_flag'


class ExtFail2Ban(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    proto = models.CharField(max_length=50)
    internal = models.IntegerField()
    block_fail = models.IntegerField()
    block_unexists = models.IntegerField()
    block_minute = models.IntegerField()
    update_time = models.DateTimeField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_fail2ban'


class ExtFail2BanBlock(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    ip = models.CharField(max_length=50, blank=True, null=True)
    expire_time = models.IntegerField()
    update_time = models.DateTimeField(blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_fail2ban_block'


class ExtFail2BanTrust(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    ip = models.CharField(max_length=50, blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_fail2ban_trust'


class ExtForward(models.Model):
    mailbox_id = models.IntegerField()
    domain_id = models.IntegerField()
    mailbox = models.CharField(max_length=200, blank=True, null=True)
    rule_id = models.IntegerField()
    sequence = models.IntegerField()
    forward = models.TextField(blank=True, null=True)
    visible = models.CharField(max_length=2)
    keep_mail = models.CharField(max_length=2)
    disabled = models.CharField(max_length=2)
    local = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ext_forward'


class ExtImapmail(models.Model):
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(max_length=150, blank=True, null=True)
    src_mailbox = models.CharField(max_length=150, blank=True, null=True)
    src_server = models.CharField(max_length=100, blank=True, null=True)
    ssl = models.IntegerField()
    src_password = models.CharField(max_length=50, blank=True, null=True)
    src_folder = models.CharField(max_length=100, blank=True, null=True)
    set_from = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    last_update = models.DateTimeField()
    desc_msg = models.TextField(blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_imapmail'
        unique_together = (('mailbox_id', 'src_mailbox'),)


class ExtLdapList(models.Model):
    domain_id = models.IntegerField()
    type = models.CharField(max_length=20)
    server_domain = models.CharField(max_length=100, blank=True, null=True)
    server = models.CharField(max_length=100, blank=True, null=True)
    port = models.IntegerField()
    account = models.CharField(max_length=200, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    ou = models.CharField(max_length=500, blank=True, null=True)
    create_acct = models.CharField(max_length=50)
    create_dept = models.CharField(max_length=50)
    remark = models.TextField(blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_ldap_list'


class ExtLdapRecord(models.Model):
    domain_id = models.IntegerField()
    type = models.CharField(max_length=20)
    server_domain = models.CharField(max_length=100, blank=True, null=True)
    server = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    mailbox = models.CharField(max_length=200, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_ldap_record'
        unique_together = (('domain_id', 'type', 'mailbox'), ('domain_id', 'type', 'username'),)


class ExtList(models.Model):
    domain_id = models.IntegerField()
    listname = models.CharField(max_length=35, blank=True, null=True)
    listtype = models.CharField(max_length=7)
    dept_id = models.IntegerField()
    permission = models.CharField(max_length=7)
    address = models.CharField(max_length=200, blank=True, null=True)
    showorder = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ext_list'


class ExtListMember(models.Model):
    domain_id = models.IntegerField()
    list_id = models.IntegerField()
    address = models.CharField(max_length=80, blank=True, null=True)
    permit = models.CharField(max_length=2)
    name = models.CharField(max_length=200)
    update_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_list_member'


class ExtLogActive(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    name = models.CharField(max_length=200, blank=True, null=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    total_count = models.IntegerField()
    total_flow = models.IntegerField()
    in_count = models.IntegerField()
    in_flow = models.IntegerField()
    out_count = models.IntegerField()
    out_flow = models.IntegerField()
    spam_count = models.IntegerField()
    spam_flow = models.IntegerField()
    success_count = models.IntegerField()
    success_flow = models.IntegerField()
    failure_count = models.IntegerField()
    failure_flow = models.IntegerField()
    spam_ratio = models.CharField(max_length=10, blank=True, null=True)
    success_ratio = models.CharField(max_length=10, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_log_active'
        unique_together = (('domain_id', 'mailbox_id', 'key'),)


class ExtLogReport(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    type = models.CharField(max_length=50)
    key = models.CharField(max_length=100, blank=True, null=True)
    data = models.CharField(max_length=2000, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_log_report'
        unique_together = (('domain_id', 'mailbox_id', 'type', 'key'),)


class ExtMailDeliverStatus(models.Model):
    mailbox_id = models.IntegerField()
    main_id = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    recipient = models.CharField(max_length=200)
    folder = models.CharField(max_length=200)
    filename = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    recall_status = models.CharField(max_length=20, blank=True, null=True)
    message_id = models.CharField(max_length=200)
    deliver_time = models.DateTimeField(blank=True, null=True)
    recall_time = models.DateTimeField(blank=True, null=True)
    inform = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_mail_deliver_status'
        unique_together = (('mailbox_id', 'main_id', 'recipient'),)


class ExtMailboxExtra(models.Model):
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(max_length=80)
    size = models.IntegerField()
    type = models.CharField(max_length=20)
    data = models.CharField(max_length=500)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ext_mailbox_extra'
        unique_together = (('mailbox_id', 'type'),)


class ExtMailboxSize(models.Model):
    mailbox_id = models.IntegerField(primary_key=True)
    mailbox = models.CharField(max_length=80)
    size = models.IntegerField()
    per = models.IntegerField()
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ext_mailbox_size'


class ExtMaillog(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    datetime = models.DateTimeField()
    operate = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_maillog'


class ExtOrgLandz(models.Model):
    dept_id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField(blank=True, null=True)
    number = models.CharField(unique=True, max_length=100)
    senumber = models.CharField(max_length=100)
    parent_number = models.CharField(max_length=100, blank=True, null=True)
    parent_senumber = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=600, blank=True, null=True)
    longname = models.CharField(max_length=600, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_org_landz'


class ExtPersonLandz(models.Model):
    email_id = models.IntegerField(primary_key=True)
    number = models.CharField(unique=True, max_length=100)
    org_number = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    office_phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    qq = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    posname = models.CharField(max_length=250, blank=True, null=True)
    jobname = models.CharField(max_length=250, blank=True, null=True)
    has_resign = models.IntegerField(blank=True, null=True)
    has_delete = models.IntegerField(blank=True, null=True)
    resign_date = models.DateTimeField()
    delete_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ext_person_landz'


class ExtPopmail(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    src_mailbox = models.CharField(max_length=50, blank=True, null=True)
    src_server = models.CharField(max_length=50, blank=True, null=True)
    src_password = models.CharField(max_length=50, blank=True, null=True)
    src_keepmail = models.CharField(max_length=2)
    dst_mailbox = models.CharField(max_length=50, blank=True, null=True)
    dst_folder = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20)
    desc_msg = models.TextField(blank=True, null=True)
    lasttime = models.DateTimeField()
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ext_popmail'


class ExtPostTransfer(models.Model):
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(max_length=200, blank=True, null=True)
    server = models.CharField(max_length=200, blank=True, null=True)
    account = models.CharField(max_length=200, blank=True, null=True)
    recipient = models.CharField(max_length=200, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True, null=True)
    ssl = models.IntegerField()
    auth = models.IntegerField()
    fail_report = models.CharField(max_length=200, blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_post_transfer'


class ExtReply(models.Model):
    mailbox_id = models.IntegerField()
    domain_id = models.IntegerField()
    address = models.CharField(max_length=200, blank=True, null=True)
    rule_id = models.IntegerField()
    sequence = models.IntegerField()
    body = models.TextField(blank=True, null=True)
    work_mode = models.CharField(max_length=5)
    work_start = models.DateTimeField()
    work_end = models.DateTimeField()
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ext_reply'


class ExtReview(models.Model):
    domain = models.CharField(max_length=50, blank=True, null=True)
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    target = models.CharField(max_length=30, blank=True, null=True)
    target_id = models.IntegerField()
    workmode = models.CharField(max_length=8)
    disabled = models.CharField(max_length=2)
    option = models.CharField(max_length=2000)
    has_attach = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_review'


class ExtReviewMail(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    ident = models.CharField(max_length=25, blank=True, null=True)
    datetime = models.DateTimeField()
    sender = models.CharField(max_length=80, blank=True, null=True)
    recipient = models.TextField(blank=True, null=True)
    mailsize = models.IntegerField()
    subject = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.IntegerField(blank=True, null=True)
    savepath = models.TextField(blank=True, null=True)
    mailbody = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=6)
    reviewer_id = models.CharField(max_length=80)
    permit_address = models.CharField(max_length=250)
    reject_address = models.CharField(max_length=250)
    review_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ext_review_mail'


class ExtReviewNew(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    next_id = models.IntegerField()
    master_review = models.IntegerField()
    assist_review = models.IntegerField(blank=True, null=True)
    wait_next_time = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_review_new'


class ExtReviewNewCondition(models.Model):
    rule_id = models.IntegerField()
    option = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=20, blank=True, null=True)
    value = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ext_review_new_condition'


class ExtReviewNewProcess(models.Model):
    review_id = models.IntegerField()
    mail_id = models.IntegerField()
    reviewer_id = models.IntegerField()
    type = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    reason = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ext_review_new_process'
        unique_together = (('reviewer_id', 'mail_id'),)


class ExtReviewNewRule(models.Model):
    review_id = models.IntegerField()
    name = models.CharField(max_length=250, blank=True, null=True)
    workmode = models.CharField(max_length=20)
    cond_logic = models.CharField(max_length=20, blank=True, null=True)
    logic = models.CharField(max_length=20, blank=True, null=True)
    pre_action = models.CharField(max_length=20, blank=True, null=True)
    target_dept = models.IntegerField()
    sequence = models.IntegerField()
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_review_new_rule'


class ExtSearchData(models.Model):
    mailbox_id = models.IntegerField()
    search_type = models.CharField(max_length=50, blank=True, null=True)
    search_key = models.CharField(max_length=150, blank=True, null=True)
    folder = models.CharField(max_length=500, blank=True, null=True)
    imap_id = models.IntegerField()
    sender = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    size = models.IntegerField()
    send_date = models.DateTimeField()
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ext_search_data'


class ExtSearchResult(models.Model):
    mailbox_id = models.IntegerField(unique=True)
    search_type = models.CharField(max_length=50)
    search_key = models.CharField(max_length=150)
    page = models.IntegerField()
    total_cnt = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_search_result'


class ExtSecretMail(models.Model):
    id = models.IntegerField()
    secret_grade = models.CharField(max_length=1)
    mailbox_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_secret_mail'


class ExtSequesterMail(models.Model):
    ident = models.CharField(max_length=25, blank=True, null=True)
    datetime = models.DateTimeField()
    sender = models.CharField(max_length=80, blank=True, null=True)
    recipient = models.TextField(blank=True, null=True)
    mailsize = models.IntegerField()
    subject = models.CharField(max_length=300, blank=True, null=True)
    attachment = models.IntegerField(blank=True, null=True)
    savepath = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10)
    reason = models.CharField(max_length=50)
    detail = models.TextField()

    class Meta:
        managed = False
        db_table = 'ext_sequester_mail'


class ExtSmsWhitelist(models.Model):
    mailbox_id = models.IntegerField()
    domain_id = models.IntegerField()
    address = models.CharField(max_length=80, blank=True, null=True)
    enabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ext_sms_whitelist'


class ExtSmtpTransfer(models.Model):
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(max_length=200, blank=True, null=True)
    server = models.CharField(max_length=200, blank=True, null=True)
    account = models.CharField(max_length=200, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True, null=True)
    ssl = models.IntegerField()
    auth = models.IntegerField()
    fail_report = models.CharField(max_length=200, blank=True, null=True)
    disabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ext_smtp_transfer'


class ExtTranslateHeader(models.Model):
    domain_id = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=2)
    rule = models.CharField(max_length=250, blank=True, null=True)
    trans_value = models.CharField(max_length=250, blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'ext_translate_header'


class OabShare(models.Model):
    domain_id = models.IntegerField()
    view_target_id = models.IntegerField()
    is_default = models.IntegerField()
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'oab_share'


class PermMypermission(models.Model):
    parent_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=50)
    is_nav = models.IntegerField()
    nav_name = models.CharField(max_length=50)
    url = models.CharField(max_length=150, blank=True, null=True)
    is_default = models.IntegerField()
    order_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'perm_mypermission'


class ProxyAccount(models.Model):
    acct_id = models.IntegerField(primary_key=True)
    router_id = models.IntegerField()
    birth_server = models.IntegerField()
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(unique=True, max_length=200)
    acct_server = models.IntegerField()
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'proxy_account'


class ProxyAccountInfo(models.Model):
    acct_id = models.IntegerField(primary_key=True)
    acct_server = models.IntegerField()
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(unique=True, max_length=200, blank=True, null=True)
    name = models.CharField(max_length=35)
    domain_id = models.IntegerField(blank=True, null=True)
    domain = models.CharField(max_length=50, blank=True, null=True)
    dept_id = models.IntegerField(blank=True, null=True)
    dept_name = models.CharField(max_length=100, blank=True, null=True)
    dept_position = models.CharField(max_length=35, blank=True, null=True)
    last_update = models.DateTimeField()
    update_from = models.CharField(max_length=40, blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'proxy_account_info'
        unique_together = (('mailbox_id', 'acct_server'),)


class ProxyAccountMove(models.Model):
    acct_id = models.IntegerField(unique=True)
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(unique=True, max_length=200, blank=True, null=True)
    old_mailbox = models.CharField(max_length=200, blank=True, null=True)
    from_server = models.IntegerField()
    target_server = models.IntegerField()
    from_ip = models.CharField(max_length=20)
    target_ip = models.CharField(max_length=20)
    move_type = models.CharField(max_length=20)
    sync_mail = models.IntegerField()
    status = models.CharField(max_length=20)
    last_update = models.DateTimeField()
    data = models.TextField(blank=True, null=True)
    desc_msg = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proxy_account_move'
        unique_together = (('from_server', 'mailbox_id'), ('from_server', 'mailbox'),)


class ProxyAcctSyncErr(models.Model):
    type = models.CharField(max_length=20)
    address = models.CharField(max_length=200, blank=True, null=True)
    conflict_type = models.CharField(max_length=20)
    conflict_server = models.IntegerField(blank=True, null=True)
    conflict_name = models.CharField(max_length=120, blank=True, null=True)
    conflict_ip = models.CharField(max_length=20, blank=True, null=True)
    last_update = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proxy_acct_sync_err'
        unique_together = (('type', 'address'),)


class ProxyAcctSyncLog(models.Model):
    src_id = models.IntegerField()
    server_num = models.IntegerField()
    type = models.CharField(max_length=20)
    address = models.CharField(max_length=200, blank=True, null=True)
    from_ip = models.CharField(max_length=20, blank=True, null=True)
    ip_name = models.CharField(max_length=120)
    status = models.CharField(max_length=20)
    last_update = models.DateTimeField()
    domain_id = models.IntegerField()
    ext_data = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proxy_acct_sync_log'
        unique_together = (('src_id', 'server_num', 'type'),)


class ProxyCoreAlias(models.Model):
    src_id = models.IntegerField()
    server_num = models.IntegerField()
    type = models.CharField(max_length=20)
    source = models.CharField(unique=True, max_length=200, blank=True, null=True)
    last_update = models.DateTimeField()
    update_from = models.CharField(max_length=40)
    domain_id = models.IntegerField()
    target = models.TextField(blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'proxy_core_alias'
        unique_together = (('src_id', 'server_num'),)


class ProxyCoreBlacklist(models.Model):
    src_id = models.IntegerField()
    server_num = models.IntegerField()
    operator = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    email = models.CharField(max_length=60, blank=True, null=True)
    add_time = models.IntegerField()
    last_update = models.DateTimeField()
    update_from = models.CharField(max_length=40)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'proxy_core_blacklist'
        unique_together = (('src_id', 'server_num'),)


class ProxyCoreTrustip(models.Model):
    src_id = models.IntegerField()
    server_num = models.IntegerField()
    ip = models.CharField(max_length=48, blank=True, null=True)
    last_update = models.DateTimeField()
    update_from = models.CharField(max_length=40)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'proxy_core_trustip'
        unique_together = (('src_id', 'server_num'),)


class ProxyCoreWhitelist(models.Model):
    src_id = models.IntegerField()
    server_num = models.IntegerField()
    operator = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    email = models.CharField(max_length=60, blank=True, null=True)
    add_time = models.IntegerField()
    last_update = models.DateTimeField()
    update_from = models.CharField(max_length=40)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'proxy_core_whitelist'
        unique_together = (('src_id', 'server_num'),)


class ProxyDelLog(models.Model):
    acct_id = models.IntegerField(primary_key=True)
    acct_server = models.IntegerField()
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(max_length=200)
    delete_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'proxy_del_log'


class ProxyExtList(models.Model):
    src_id = models.IntegerField()
    server_num = models.IntegerField()
    listname = models.CharField(max_length=35, blank=True, null=True)
    listtype = models.CharField(max_length=20)
    dept_id = models.IntegerField()
    permission = models.CharField(max_length=20)
    address = models.CharField(unique=True, max_length=200, blank=True, null=True)
    showorder = models.IntegerField()
    last_update = models.DateTimeField()
    update_from = models.CharField(max_length=40)
    domain_id = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    disabled = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'proxy_ext_list'
        unique_together = (('src_id', 'server_num'),)


class ProxyNewCreate(models.Model):
    mailbox_id = models.IntegerField(primary_key=True)
    mailbox = models.CharField(unique=True, max_length=200, blank=True, null=True)
    acct_id = models.IntegerField()
    router_id = models.IntegerField()
    register_succ = models.CharField(max_length=1)
    register_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'proxy_new_create'


class ProxyRedisCache(models.Model):
    name = models.CharField(primary_key=True, max_length=80)
    type = models.CharField(max_length=20)
    data = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proxy_redis_cache'


class ProxyRedisLog(models.Model):
    type = models.IntegerField()
    exec_type = models.CharField(max_length=10)
    data = models.CharField(max_length=300)
    save_status = models.IntegerField(blank=True, null=True)
    exec_status = models.IntegerField(blank=True, null=True)
    protocol = models.CharField(max_length=50)
    add_time = models.IntegerField()
    update_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'proxy_redis_log'


class ProxyRouterTable(models.Model):
    router_id = models.AutoField(primary_key=True)
    server_num = models.IntegerField()
    acct_idx = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'proxy_router_table'


class ProxyServerConfig(models.Model):
    config_name = models.CharField(unique=True, max_length=40)
    config_data = models.CharField(max_length=250)
    ext = models.CharField(max_length=100)
    pwd = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'proxy_server_config'


class ProxyServerList(models.Model):
    server_num = models.AutoField(primary_key=True)
    server_name = models.CharField(max_length=120)
    server_ip = models.CharField(max_length=20)
    disabled = models.CharField(max_length=2)
    is_master = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proxy_server_list'


class ProxyServerStatus(models.Model):
    server_num = models.IntegerField(primary_key=True)
    status_conn = models.CharField(max_length=20)
    status_recv = models.CharField(max_length=20)
    reject_reason = models.CharField(max_length=500)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'proxy_server_status'


class ProxyVerifyIp(models.Model):
    server_num = models.IntegerField()
    server_ip = models.CharField(max_length=30, blank=True, null=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'proxy_verify_ip'
        unique_together = (('server_num', 'server_ip'),)


class ProxyVersionLog(models.Model):
    version = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'proxy_version_log'


class WidgetCogroup(models.Model):
    groupno = models.IntegerField(primary_key=True)
    groupname = models.CharField(max_length=60, blank=True, null=True)
    domain_id = models.IntegerField()
    dept_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'widget_cogroup'


class WidgetCogroupMember(models.Model):
    groupno = models.IntegerField()
    mobile = models.CharField(max_length=20, blank=True, null=True)
    oauid = models.IntegerField()
    oaname = models.CharField(max_length=35, blank=True, null=True)
    mailbox_id = models.IntegerField()
    isadmin = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'widget_cogroup_member'
        unique_together = (('groupno', 'mailbox_id'),)


class WidgetScoreStat(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField(unique=True)
    score = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'widget_score_stat'


class WidgetScoreType(models.Model):
    domain_id = models.IntegerField()
    operate = models.CharField(max_length=35, blank=True, null=True)
    score = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'widget_score_type'
        unique_together = (('domain_id', 'operate'),)


class WmAddrbookContact(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    fullname = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField()
    email = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    im_qq = models.CharField(max_length=25, blank=True, null=True)
    im_msn = models.CharField(max_length=50, blank=True, null=True)
    homepage = models.CharField(max_length=50, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    home_country = models.CharField(max_length=50, blank=True, null=True)
    home_state = models.CharField(max_length=50, blank=True, null=True)
    home_city = models.CharField(max_length=50, blank=True, null=True)
    home_address = models.CharField(max_length=100, blank=True, null=True)
    home_tel = models.CharField(max_length=15, blank=True, null=True)
    home_zip = models.CharField(max_length=15, blank=True, null=True)
    work_name = models.CharField(max_length=50, blank=True, null=True)
    work_dept = models.CharField(max_length=50, blank=True, null=True)
    work_position = models.CharField(max_length=50, blank=True, null=True)
    work_address = models.CharField(max_length=100, blank=True, null=True)
    work_zip = models.CharField(max_length=15, blank=True, null=True)
    work_tel = models.CharField(max_length=15, blank=True, null=True)
    work_fax = models.CharField(max_length=15, blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wm_addrbook_contact'


class WmAddrbookEmail(models.Model):
    contact_id = models.IntegerField(unique=True)
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    email = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wm_addrbook_email'


class WmAddrbookGroup(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    groupname = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wm_addrbook_group'


class WmAddrbookMap(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    group_id = models.IntegerField()
    contact_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wm_addrbook_map'
        unique_together = (('mailbox_id', 'group_id', 'contact_id'),)


class WmCalendar(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    event_date = models.DateField()
    event_time = models.TimeField()
    is_allday = models.CharField(max_length=2)
    due_date = models.DateField()
    due_time = models.TimeField()
    subject = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    place = models.CharField(max_length=32, blank=True, null=True)
    is_repeat = models.CharField(max_length=2)
    repeat_type = models.CharField(max_length=5)
    repeat_frequency = models.IntegerField()
    repeat_end = models.DateField()

    class Meta:
        managed = False
        db_table = 'wm_calendar'


class WmCalendarGroup(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    group_name = models.CharField(max_length=64)
    permission = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'wm_calendar_group'


class WmCalendarGroupMember(models.Model):
    domain_id = models.IntegerField()
    group_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    mailbox = models.CharField(max_length=100, blank=True, null=True)
    permission = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'wm_calendar_group_member'


class WmCalendarShare(models.Model):
    domain_id = models.IntegerField()
    event_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    status = models.CharField(max_length=6)
    permission = models.CharField(max_length=4)
    verify_code = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wm_calendar_share'


class WmCustomerCate(models.Model):
    cate_id = models.AutoField(primary_key=True)
    domain_id = models.IntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    parent_id = models.IntegerField()
    order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wm_customer_cate'


class WmCustomerInfo(models.Model):
    customer_id = models.AutoField(primary_key=True)
    domain_id = models.IntegerField()
    cate_id = models.CharField(max_length=255)
    fullname = models.CharField(max_length=30, blank=True, null=True)
    gender = models.CharField(max_length=1)
    birthday = models.DateField()
    pref_email = models.CharField(max_length=50, blank=True, null=True)
    pref_tel = models.CharField(max_length=18, blank=True, null=True)
    im_qq = models.CharField(max_length=25, blank=True, null=True)
    im_msn = models.CharField(max_length=50, blank=True, null=True)
    home_tel = models.CharField(max_length=15, blank=True, null=True)
    work_tel = models.CharField(max_length=15, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wm_customer_info'


class WmNetdiskFiles(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    folder_id = models.IntegerField()
    file_name = models.CharField(max_length=150, blank=True, null=True)
    file_path = models.CharField(max_length=100, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    file_suffix = models.CharField(max_length=10, blank=True, null=True)
    file_size = models.IntegerField()
    created = models.DateTimeField()
    sharetime_end = models.IntegerField()
    online_attach_time = models.IntegerField()
    share_code = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wm_netdisk_files'


class WmNetdiskFolder(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    parent_id = models.IntegerField()
    name = models.CharField(max_length=150, blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wm_netdisk_folder'


class WmNoteCategory(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    name = models.CharField(max_length=30, blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wm_note_category'


class WmNoteContent(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    cate_id = models.IntegerField()
    title = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wm_note_content'


class WmRelateEmail(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    target_id = models.IntegerField()
    target_pass = models.CharField(max_length=64, blank=True, null=True)
    access = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'wm_relate_email'


class WmSignature(models.Model):
    domain_id = models.IntegerField()
    mailbox_id = models.IntegerField()
    type = models.CharField(max_length=20)
    caption = models.CharField(max_length=35, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    default = models.CharField(max_length=2)
    refw_default = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'wm_signature'


class WmStatistics(models.Model):
    mailbox_id = models.IntegerField()
    domain_id = models.IntegerField()
    last_login_time = models.DateTimeField()
    last_login_addr = models.CharField(max_length=25, blank=True, null=True)
    last_refresh_time = models.DateTimeField()
    last_refresh_addr = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wm_statistics'


class WmTemplate(models.Model):
    domain_id = models.IntegerField()
    name = models.CharField(max_length=35, blank=True, null=True)
    image = models.CharField(max_length=35, blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wm_template'


class WxApiLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    way = models.CharField(max_length=30)
    status = models.IntegerField()
    message = models.CharField(max_length=2500)
    add_time = models.IntegerField()
    data = models.CharField(max_length=2000)
    clinet_ip = models.CharField(max_length=50)
    server_ip = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'wx_api_log'


class WxConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    token = models.CharField(max_length=200)
    appid = models.CharField(max_length=50)
    appsecret = models.CharField(max_length=200)
    access_token = models.TextField()
    dateline = models.IntegerField()
    jsapi_ticket = models.TextField(blank=True, null=True)
    jsapiline = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=200)
    agentid = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'wx_config'


class WxMsg(models.Model):
    id = models.BigAutoField(primary_key=True)
    unionid = models.CharField(max_length=200)
    openid = models.CharField(max_length=150)
    temp_id = models.CharField(max_length=150)
    data = models.CharField(max_length=1000)
    status = models.IntegerField()
    url = models.CharField(max_length=300)
    update_time = models.IntegerField()
    add_time = models.IntegerField()
    message = models.CharField(max_length=300, blank=True, null=True)
    ip = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wx_msg'


class WxSmsCode(models.Model):
    phone = models.CharField(max_length=25)
    code = models.CharField(max_length=10)
    status = models.IntegerField()
    type = models.IntegerField()
    add_time = models.IntegerField()
    update_time = models.IntegerField()
    ip = models.CharField(max_length=50)
    ext = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'wx_sms_code'


class WxTemplate(models.Model):
    temp_id = models.CharField(max_length=200)
    type = models.IntegerField()
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'wx_template'
        unique_together = (('type', 'code'),)


class WxTemplateField(models.Model):
    field_name = models.CharField(max_length=100)
    field_val = models.CharField(max_length=200)
    template_id = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'wx_template_field'
        unique_together = (('field_name', 'template_id'),)


class WxUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    openid = models.CharField(max_length=128)
    unionid = models.CharField(max_length=255)
    nickname = models.CharField(max_length=300)
    img = models.CharField(max_length=700)
    update_time = models.IntegerField()
    add_time = models.IntegerField()
    subscribe = models.IntegerField()
    subscribe_time = models.IntegerField()
    city = models.CharField(max_length=80)
    province = models.CharField(max_length=100)
    remark = models.CharField(max_length=2000)
    userid = models.CharField(db_column='UserId', max_length=100)  # Field name made lowercase.
    deviceid = models.CharField(db_column='DeviceId', max_length=100)  # Field name made lowercase.
    expires_in = models.IntegerField()
    user_ticket = models.CharField(max_length=200)
    department = models.CharField(max_length=20)
    position = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20)
    gender = models.IntegerField()
    email = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wx_user'
        unique_together = (('openid', 'userid', 'deviceid'),)


class WxUserSwitch(models.Model):
    mailbox_id = models.IntegerField(primary_key=True)
    new_mail_sms = models.IntegerField()
    new_mail_wx = models.IntegerField()
    change_pwd_sms = models.IntegerField()
    change_pwd_wx = models.IntegerField()
    capacity_sms = models.IntegerField()
    capacity_wx = models.IntegerField()
    reset_pwd_sms = models.IntegerField()
    reset_pwd_wx = models.IntegerField()
    update_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wx_user_switch'
