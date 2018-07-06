#coding=utf-8
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

KB = 1 << 10
MB = 1 << 20
GB = 1 << 30
TB = 1 << 40
PB = 1 << 50

ATTACH_SAVE_PATH = settings.ATTACH_DATA_PATH
TEMP_SAVE_PATH = settings.TEMP_DATA_PATH
EDM_WEB_URL = settings.EDM_WEB_URL

UPLOAD_ALLOWED_SUFFIX = [
    'gif', 'jpg', 'jpeg', 'png', 'bmp',
    'txt', 'pdf', 'doc', 'docx',
    'xls','xlsx','csv',
    'ppt','pps','pptx','ppsx', 'htm','html',
    'zip','rar','gz','bz2','ics',
]

# KindEditor 上传文件后缀
UPLOAD_JSON_SUFFIX = {
    'image' : ['gif', 'jpg', 'jpeg', 'png', 'bmp'],
    'flash' : ['swf', 'flv'],
    'media' : ['swf', 'flv', 'mp3', 'wav', 'wma', 'wmv', 'mid', 'avi', 'mpg', 'asf', 'rm', 'rmvb'],
    'file'  : ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'htm', 'html', 'txt', 'zip', 'rar', 'gz', 'bz2'],
}

# 主题插入变量配置
SUBJECT_VARS = (
    ('{FULLNAME}', _(u'收件人姓名')),
    ('{RECIPIENTS}',  _(u'收件人地址')),
    ('{DATE}',  _(u'当前日期')),
    ('{RANDOM_NUMBER}',  _(u'随机10位数字')),
    ('{SEX}', _(u'性别')),
    ('{BIRTHDAY}', _(u'生日')),
    ('{PHONE}', _(u'手机')),
    ('{AREA}', _(u'地区')),
    ('{VAR1}', _(u'变量1')),
    ('{VAR2}', _(u'变量2')),
    ('{VAR3}', _(u'变量3')),
    ('{VAR4}', _(u'变量4')),
    ('{VAR5}', _(u'变量5')),
    ('{VAR6}', _(u'变量6')),
    ('{VAR7}', _(u'变量7')),
    ('{VAR8}', _(u'变量8')),
    ('{VAR9}', _(u'变量9')),
    ('{VAR10}', _(u'变量10')),
)

CONTENT_TYPE = (
    (1, _(u'编辑HTML模板')),
    (2, _(u'上传EML邮件文件')),
)

ENCODING_TYPE = (
    ('base64', u'base64'),
    ('quoted-printable', u'quoted-printable'),
)

CHARACTER_TYPE = (
    ('utf-8', u'utf-8'),
    #('iso-8859-1', u'iso-8859-1'),
    ('gb18030', u'gb18030'),
    #('euc-jp', u'euc-jp'),
)

IMAGE_TYPE = (
    ('N', _(u'否')),
    ('Y', _(u'是')),
)

ATTACH_TYPE = (
    ('common', _(u'传统内嵌附件')),
    ('html', _(u'在线附件')),
)

PRIORITY_TYPE = (
    ('low', _(u'普通')),
    ('middle', _(u'较高')),
    ('high', _(u'最高')),
)

RESULT_TYPE = (
    ('green', _(u'安全')),
    ('red', _(u'危险')),
    ('red_pass', _(u'危险')),
    ('yellow', _(u'警告')),
)

STATUS = (
    ('0', _(u'启用')),
    ('1', _(u'禁用')),
)

INT_STATUS = (
    (0, _(u'禁用')),
    (1, _(u'启用')),
)

EDIT_TYPE = (
    ('1', _(u'在线编辑')),
    ('2', _(u'从网址导入')),
    ('3', _(u'从html文件导入')),
    ('4', _(u'从eml文件导入')),
    ('5', _(u'从压缩文件导入')),
)

TEST_STATUS = (
    (0, _(u'发送失败')),
    (1, _(u'发送成功')),
    (2, _(u'正在发送')),
)

TEST_USER_TYPE = (
    ('users', _(u'客户')),
    ('manager', _(u'管理员')),
)

