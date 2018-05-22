#coding=utf-8
from __future__ import unicode_literals
from django.db import models

def get_open_email_statistics_model(date):
    class OpenEmailStatisticsMetaClass(models.base.ModelBase):
        def __new__(cls, name, bases, attrs):
            model = super(OpenEmailStatisticsMetaClass, cls).__new__(cls, name, bases, attrs)
            model._meta.db_table = 'open_email_statistics_{}'.format(date)
            return model

    class OpenEmailStatistics(models.Model):
        __metaclass__ = OpenEmailStatisticsMetaClass

        email = models.CharField(u'邮箱', max_length=100, null=False, blank=False, unique=True)
        hits = models.IntegerField(u'打开数', null=False, blank=False, default=0)
        isvalid = models.BooleanField(u'是否处理了', default=False)

    return OpenEmailStatistics


class EmailOpenClickTemp(models.Model):
    email = models.CharField(u'邮箱', max_length=100, null=False, blank=False, db_index=True)
    opens = models.IntegerField(u'打开数', null=False, blank=False, default=0)
    clicks = models.IntegerField(u'点击数', null=False, blank=False, default=0)
    activity = models.IntegerField(u'活跃度', null=False, blank=False, default=0)

    def __unicode__(self):
        return self.email

    class Meta:
        managed = False
        db_table = 'email_open_click_temp'


class EmailOpenClick(models.Model):
    email = models.CharField(u'邮箱', max_length=100, null=False, blank=False, unique=True)
    opens = models.IntegerField(u'打开数', null=False, blank=False, default=0)
    clicks = models.IntegerField(u'点击数', null=False, blank=False, default=0)
    activity = models.IntegerField(u'活跃度', null=False, blank=False, default=0)

    def __unicode__(self):
        return self.email

    class Meta:
        managed = False
        db_table = 'email_open_click'


class EmailActivitySettings(models.Model):
    level = models.IntegerField(u'星级', null=False, blank=False, default=1, unique=True)
    open_low = models.IntegerField(u'最低打开数', null=False, blank=False, default=0)
    open_high = models.IntegerField(u'最高打开数', null=False, blank=False, default=0)
    click_low = models.IntegerField(u'最低点击数', null=False, blank=False, default=0)
    click_high = models.IntegerField(u'最高点击数', null=False, blank=False, default=0)

    def __unicode__(self):
        return self.level

    class Meta:
        managed = False
        db_table = 'email_activity_settings'


# """
# CREATE TABLE "email_activity_settings" (
#     "id" serial NOT NULL PRIMARY KEY,
#     "email" varchar(100) NOT NULL,
#     "level" integer NOT NULL UNIQUE,
#     "open_low" integer NOT NULL,
#     "open_high" integer NOT NULL,
#     "click_low" integer NOT NULL,
#     "click_high" integer NOT NULL,
#     "isvalid" boolean NOT NULL
# );
# """

class AdressPool(models.Model):
    email = models.CharField(u'邮箱', max_length=100, null=False, blank=False, unique=True)
    fullname = models.CharField(u'姓名', max_length=100, null=True, blank=True)
    sex = models.CharField(u'性别', max_length=8, null=True, blank=True)
    birthday = models.DateField(verbose_name='生日', blank=True, null=True)
    phone = models.CharField(u'手机', max_length=100, null=True, blank=True)
    area = models.CharField(u'所在地域', max_length=200, null=True, blank=True)
    updated = models.DateTimeField(u'更新时间', auto_now=True)
    var1 = models.CharField(u'变量1', max_length=100, null=True, blank=True)
    var2 = models.CharField(u'变量2', max_length=100, null=True, blank=True)
    var3 = models.CharField(u'变量3', max_length=100, null=True, blank=True)
    var4 = models.CharField(u'变量4', max_length=100, null=True, blank=True)
    var5 = models.CharField(u'变量5', max_length=100, null=True, blank=True)
    var6 = models.CharField(u'变量6', max_length=100, null=True, blank=True)
    var7 = models.CharField(u'变量7', max_length=100, null=True, blank=True)
    var8 = models.CharField(u'变量8', max_length=100, null=True, blank=True)
    var9 = models.CharField(u'变量9', max_length=100, null=True, blank=True)
    var10 = models.CharField(u'变量10', max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.email

    class Meta:
        managed = False
        db_table = 'core_address'

OTHER_TAG_CATEGORY = (
    ('address', u'地址池'),
    ('customer', u'客户'),
    ('activity', u'活跃度'),
)

class AttributePool(models.Model):
    category = models.CharField(u'分类', max_length=10, null=False, blank=False, choices=OTHER_TAG_CATEGORY)
    # parent_level = models.CharField(u'父级标签', max_length=50, null=True, blank=True)
    # attribute = models.CharField(u'子属性', max_length=100, null=True, blank=True)
    category_id = models.IntegerField(u'分类ID', default=0)
    tag_id = models.IntegerField(u'标签ID', default=0)

    def __unicode__(self):
        return self.attribute

    class Meta:
        managed = False
        # unique_together = (("category", "parent_level", "attribute"),)
        unique_together = (("category", "category_id", "tag_id"),)
        db_table = 'core_attribute'

class AdressAttributeRelation(models.Model):
    email = models.ForeignKey(AdressPool, related_name='otherAdressPool', null=False, blank=False, db_index=True)
    attribute = models.ForeignKey(AttributePool, related_name='otherAttributePool', null=False, blank=False, db_index=True)
    # remark = models.CharField(u'说明', max_length=100, null=False, blank=False)
    list_id = models.IntegerField(u'列表ID', default=0, db_index=True)
    customer_id = models.IntegerField(u'客户ID', default=0)

    class Meta:
        managed = False
        # unique_together = (("email", "attribute", "list_id"),)
        db_table = 'core_address_attribute_rel'

SEX_TYPE = (
    ('', u'无'),
    ('m', u'男'),
    ('f', u'女'),
)

class MailAnalyzeInfo(models.Model):
    ''' 邮箱分析基础信息 '''
    address = models.CharField(u'邮箱', null=False, blank=False, unique=True, max_length=100)
    name = models.CharField(u'姓名', null=True, blank=True, max_length=100)
    sex = models.CharField(u'性别', null=True, blank=True, max_length=2, choices=SEX_TYPE)
    mobilephone = models.CharField(u'移动电话', null=True, blank=True, max_length=200)
    telephone = models.CharField(u'固定电话', null=True, blank=True, max_length=200)
    company_name = models.CharField(u'公司名称(学校学院)', null=True, blank=True, max_length=200)
    post_name = models.CharField(u'岗位名称', null=True, blank=True, max_length=200)
    profession = models.CharField(u'专业名称', null=True, blank=True, max_length=200)
    describer = models.TextField(u'描述', help_text=u'记录暂未处理的记录。')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    def __unicode__(self):
        return self.address

    class Meta:
        db_table = 'email_analyze'

"""
from django.core.management import color
from django.db import connections
connection = connections['default']
style = color.no_style()
output, references = connection.creation.sql_create_model(AdressPool, style)
for a in output:
    print a
output = connection.creation.sql_indexes_for_model(AdressPool, style)
for sql in output:
    print sql
"""

"""
CREATE TABLE "core_address" (
    "id" serial NOT NULL PRIMARY KEY,
    "email" varchar(100) NOT NULL UNIQUE,
    "fullname" varchar(100),
    "sex" varchar(8),
    "birthday" date,
    "phone" varchar(100),
    "area" varchar(200),
    "updated" timestamp with time zone NOT NULL,
    "var1" varchar(100),
    "var2" varchar(100),
    "var3" varchar(100),
    "var4" varchar(100),
    "var5" varchar(100),
    "var6" varchar(100),
    "var7" varchar(100),
    "var8" varchar(100),
    "var9" varchar(100),
    "var10" varchar(100)
);
CREATE INDEX "core_address_email_like" ON "core_address" ("email" varchar_pattern_ops);

CREATE TABLE "core_address" (
    "id" serial NOT NULL PRIMARY KEY,
    "email" varchar(100) NOT NULL UNIQUE
);
CREATE INDEX "core_address_email_like" ON "core_address" ("email" varchar_pattern_ops);

CREATE TABLE "core_attribute" (
    "id" serial NOT NULL PRIMARY KEY,
    "category" varchar(10) NOT NULL,
    "parent_level" varchar(50) NOT NULL,
    "attribute" varchar(100) NOT NULL,
    UNIQUE ("category", "parent_level", "attribute")
);

CREATE TABLE "core_address_attribute_rel" (
    "id" serial NOT NULL PRIMARY KEY,
    "email_id" integer NOT NULL,
    "attribute_id" integer NOT NULL,
    "list_id" integer DEFAULT 0,
    "customer_id" integer DEFAULT 0,
    UNIQUE ("email_id", "attribute_id", "list_id")
);
CREATE INDEX "core_address_attribute_rel_email_id" ON "core_address_attribute_rel" ("email_id");
CREATE INDEX "core_address_attribute_rel_attribute_id" ON "core_address_attribute_rel" ("attribute_id");
CREATE INDEX core_address_attribute_rel_list_id ON core_address_attribute_rel USING btree (list_id);

"""





