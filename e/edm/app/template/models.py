#coding=utf-8
from __future__ import unicode_literals


import os
import math
from django.db import models
from django import template
from django.template import Context
from app.core.models import Customer, CheckSetting
from app.template.configs import ( CONTENT_TYPE, ENCODING_TYPE, CHARACTER_TYPE, IMAGE_TYPE,
                                   ATTACH_TYPE, PRIORITY_TYPE, RESULT_TYPE, STATUS, SUBJECT_VARS,
                                   ATTACH_SAVE_PATH, TEMP_SAVE_PATH, EDM_WEB_URL, INT_STATUS,
                                   KB, TEST_STATUS, TEST_USER_TYPE )
from lib.template import del_filepath, get_render_attach_template, MulTemplateEmail
from app.template.utils.formats import filesizeformat

from django.utils.translation import ugettext_lazy as _

##### 模板 #####
class SendTemplate(models.Model):
    id = models.AutoField(primary_key=True, db_column='template_id')
    user = models.ForeignKey(Customer, related_name='Customer01', db_index=True, null=False, blank=False)
    content_type = models.SmallIntegerField(u'模板类型', choices=CONTENT_TYPE, default=1)
    name = models.CharField(u'模板名称', null=True, blank=True, max_length=100)
    subject = models.CharField(u'邮件主题', null=True, blank=True, max_length=100)
    content = models.TextField(u'HTML内容', null=True, blank=True)
    text_content = models.TextField(u'文本内容', null=True, blank=True, help_text=u'文本形式的邮件内容')
    encoding = models.CharField(_(u'邮件编码'), max_length=50, null=False, blank=False, choices=ENCODING_TYPE, default='base64')
    character = models.CharField(_(u'转换字符集'), max_length=32, null=False, blank=False, choices=CHARACTER_TYPE, default='utf-8')
    image_encode = models.CharField(_(u'是否内嵌照片'), max_length=32, null=False, blank=False, choices=IMAGE_TYPE, default='N',
                                    help_text=_(u'否：邮件内的图片会自动上传到U-Mail服务器上，以外部图像链接的方式显示图片。'
                                              '是：邮件所使用的图像内嵌在邮件消息中。 这将导致邮件大小的增加(扣除更多群发点数), 但是邮件却可以脱机浏览。 '))
    attachtype = models.CharField(_(u'附件设置'), max_length=32, null=False, blank=False, choices=ATTACH_TYPE, default=u'common',
                                  help_text=_(u'传统附件：以普通的邮件附件形式发送，附件大小会增加邮件大小，但是附件可以脱机查看。'
                                            u'在线附件：邮件的附件以HTML超链接的形式内嵌在邮件消息中，不会增大邮件大小，但是需要网络才可访问。 '))
    priority = models.CharField(u'优先投递级别', max_length=32, null=False, blank=False, choices=PRIORITY_TYPE, default='low',
                                help_text=u'最高投递级别将2倍扣除点数、较高投递级别将1.5倍扣除点数。')
    report = models.TextField(u'报告', null=True, blank=True)
    result = models.CharField(u'检测结果', max_length=16, null=True, blank=True, choices=RESULT_TYPE)
    spam_note = models.CharField(u'垃圾备注', max_length=100, null=True, blank=True, help_text=u'检测为垃圾模板时的备注信息')
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', null=True, auto_now=True)
    status = models.CharField(u'状态', max_length=1, null=False, blank=False, choices=STATUS, default='0')
    size = models.IntegerField(u'文本大小', default=0)
    isvalid = models.BooleanField(u'是否有效', default=True)
    issync = models.BooleanField(u'是否已同步', default=False, help_text=u'同步老系统的主题列表。')
    edm_check_result = models.CharField(u'群发垃圾检测', max_length=20, null=True, blank=True, help_text=u'被“群发垃圾检测设置”命中的ID字段')
    real_size = models.IntegerField(u'邮件大小', default=0)
    is_mosaico = models.BooleanField(u'新式模板', default=False)
    is_shield = models.BooleanField(_(u'是否被屏蔽'), default=False)

    def __unicode__(self):
        if self.name:
            if len(self.name)>30:
                return self.name[:30] + "..."
            return self.name
        return self.id
        # return self.name if self.name else self.id

    class Meta:
        managed = False
        db_table = 'ms_send_template'

    # 获取增强检测结果
    def get_edm_check_result(self):
        html = ''
        set_ids = map(int, self.edm_check_result.split(',') if self.edm_check_result else [])
        for set_id in set_ids:
            obj = CheckSetting.objects.filter(id=set_id).first()
            if obj and obj.tip:
                html += u"""
                <span class="text-danger" style="margin-left: 27px!important;">{}</span><br>
                """.format(obj.tip)
        return html

    # 组织邮件
    def organize_msg(self, mail_from=u'system@bestedm.org', mail_to=u'test@bestedm.org', reply_to=None, task_id=None, send_maillist_id=None, replace=False, is_need_receipt=False, track_domain=None, sys_track_domain=None):
        template_id = self.id if self.id else 0
        attachment = SendAttachment.objects.filter(template_id=template_id, user=self.user, attachtype='common').values_list('filepath', 'filetype', 'filename')
        m = MulTemplateEmail(content_type=self.content_type, character=self.character, encoding=self.encoding,
                             template_id=template_id, mail_from=mail_from, mail_to=mail_to, reply_to=reply_to, task_id=task_id, send_maillist_id=send_maillist_id,
                             subject=self.subject, content=self.content, text_content=self.text_content,
                             attachment=attachment, user_id=self.user_id, replace=replace, edm_check_result=self.edm_check_result, is_need_receipt=is_need_receipt,
                             track_domain=track_domain, sys_track_domain=sys_track_domain)
        return m.get_message()

    # 删除附件
    def delete_attach(self, attachtype=None, attach_id=None):
        att_obj_list = SendAttachment.objects.filter(template_id=self.id, user=self.user)
        count = 0
        if attachtype:
            att_obj_list = att_obj_list.filter(attachtype=attachtype)
        if attach_id:
            att_obj_list = att_obj_list.filter(id=attach_id)

        flag = True if self.name else False
        for att_obj in att_obj_list:
            if flag:
                if att_obj.attachtype == 'common':
                    try:
                        att_path = os.path.join(ATTACH_SAVE_PATH, str(self.id), att_obj.filepath)
                        del_filepath(att_path)
                        att_obj.delete()
                    except:
                        pass
                if att_obj.attachtype == 'html':
                    count += 1
            else:
                try:
                    att_path = os.path.join(ATTACH_SAVE_PATH, str(self.id), att_obj.filepath)
                    del_filepath(att_path)
                    att_obj.delete()
                except:
                    pass
        # 删除时，若没有网络附件则直接删除目录
        if not attachtype and not count:
            try:
                att_path = os.path.join(ATTACH_SAVE_PATH, str(self.id))
                del_filepath(att_path)
            except:
                pass
        # att_obj_list.delete()
        return True

    # 渲染附件列表模板
    def render_attach_template(self):
        lists = []
        field = ('id', 'filename', 'template_id', 'size')
        attachment = SendAttachment.objects.filter(
            template_id=self.id, user=self.user, attachtype='common'
        ).values_list('id', 'filename', 'template_id', 'size')
        for att in attachment:
            lists.append(dict(zip(field, att)))
        html = get_render_attach_template()
        t = template.Template(html)
        django_html = t.render(Context({'lists': lists}))
        return django_html

    # 获取跟踪链接的邮件大小
    def get_template_link_size(self):
        if self.real_size>0:
            return self.real_size
        return self.get_template_size()

    # 格式化模板大小
    def formate_template_link_size(self):
        return filesizeformat(self.get_template_link_size())

    # 获取模板大小
    def get_template_size(self, c_size=None):
        size = 0
        if c_size is not None:
            size = c_size
        elif self.content:
            size = len(self.content)

        att_objs = SendAttachment.objects.filter(template_id=self.id, user=self.user, attachtype='common')
        for obj in att_objs:
            size += obj.size
        # 邮件封装后大小将为邮件模板大小的基础上浮15%-30%。取1.3
        # size = size * 1.3
        return size

    # 格式化模板大小
    def formate_template_size(self):
        return filesizeformat(self.get_template_size())

    # 获取模板将要多少点数
    def get_template_point(self):
        size = round( self.get_template_link_size() / (KB * 1.000), 2 )
        return int( math.ceil( size/100 ) )

    # 动态获取显示结果
    def show_result_img(self):
        test_html = _(u'''
        <a type="button" class="btn btn-outline btn-success btn-xs" href="Javascript: send_test_template(%(template_id)d)">发送测试</a>
        <a data-toggle="modal" href="/template/test/history/%(template_id)d/" data-target="#myModal" data-whatever="" title="测试记录" type="button" class="btn btn-outline btn-info btn-xs">测试记录</a>
        ''') % {'template_id': self.id},
        if self.result == 'green':
            return (
                '1',
                _(u'''<a data-toggle="modal" href="/template/show_template_report/?template_id=%(template_id)d" data-target="#myModal" data-whatever="" title="检测结果">
                <img src="/static/img/report_green.jpg" width="16" height="16"></a>''') % {'template_id': self.id},
                test_html
            )
        elif self.result == 'yellow':
            return (
                '1',
                _(u'''<a data-toggle="modal" href="/template/show_template_report/?template_id=%(template_id)d" data-target="#myModal" data-whatever="" title="检测结果">
                <img src="/static/img/report_yellow.jpg" width="16" height="16"></a>''') % {'template_id': self.id},
                test_html
            )
        elif self.result == 'red_pass':
            return (
                '1',
                _(u'''<a data-toggle="modal" href="/template/show_template_report/?template_id=%(template_id)d" data-target="#myModal" data-whatever="" title="检测结果">
                <img src="/static/img/report_red_pass.jpg" width="16" height="16"></a>''') % {'template_id': self.id},
                test_html
            )
        elif self.result == 'red':
            return (
                '1',
                _(u'''<a data-toggle="modal" href="/template/show_template_report/?template_id=%(template_id)d" data-target="#myModal" data-whatever="" title="检测结果">
                <img src="/static/img/report_red.jpg" width="16" height="16"></a>''') % {'template_id': self.id},
                ''
            )
        elif self.result == 'red_pass':
            return (
                '1',
                _(u'''<a data-toggle="modal" href="/template/show_template_report/?template_id=%(template_id)d" data-target="#myModal" data-whatever="" title="检测结果">
                <img src="/static/img/report_red.jpg" width="16" height="16"></a>''') % {'template_id': self.id},
                ''
            )
        elif self.name:
            return ('0', _(u'检测中<img src="/static/img/loading.gif" width="16" height="16">'), '')
        else:
            return ('0', '<p>-</p>', '')

    # 需要动态检测的标记
    def bool_result_status(self):
        if self.name and not self.result:
            return True
        return False

    # 检测模板的主题列表是否存在
    def exsited_subject(self):
        subjects = self.SendTemplate02.all()
        return True if subjects else False

##### 附件 #####
class SendAttachment(models.Model):
    user = models.ForeignKey(Customer, related_name='Customer02', db_index=True, null=False, blank=False)
    template = models.ForeignKey(SendTemplate, related_name='SendTemplate01', db_index=True, null=False, blank=False)
    filename = models.CharField(u'文件名称', max_length=100, null=True, blank=True)
    filetype = models.CharField(u'文件类型', max_length=100, null=True, blank=True)
    filepath = models.CharField(u'文件路径', max_length=100, null=True, blank=True)
    attachtype =  models.CharField(u'附件设置', max_length=32, null=True, blank=True)
    size = models.IntegerField(u'附件大小', default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'ms_send_attachment'

##### 主题 #####
class SendSubject(models.Model):
    id = models.AutoField(primary_key=True, db_column='subject_id')
    template = models.ForeignKey(SendTemplate, related_name='SendTemplate02', db_index=True, null=False, blank=False)
    subject = models.CharField(u'邮件主题', null=True, blank=True, max_length=150)

    def __unicode__(self):
        return self.subject

    class Meta:
        managed = False
        db_table = 'ms_send_subject'

##### 参考模板分类 #####
class RefTemplateCategory(models.Model):
    id = models.AutoField(primary_key=True, db_column='cate_id')
    pid = models.IntegerField(default=0)
    name = models.CharField(u'名称', null=False, blank=False, max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'ms_ref_tpl_cate'

##### 参考模板 #####
class RefTemplate(models.Model):
    id = models.AutoField(primary_key=True, db_column='template_id')
    manager_id = models.IntegerField(default=0)
    agent_id = models.IntegerField(default=0)
    customer_id = models.IntegerField(default=0)
    cate = models.ForeignKey(RefTemplateCategory, related_name='RefTemplateCategory01', null=False, blank=False)
    name = models.CharField(u'模板名称', null=True, blank=True, max_length=30)
    subject = models.CharField(u'主题', null=True, blank=True, max_length=100)
    content = models.TextField(u'HTML内容', null=True, blank=True)
    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'修改时间', auto_now=True)
    status = models.IntegerField(u'状态', choices=INT_STATUS, default=0)
    thumb_path = models.CharField(u'路径', null=True, blank=True, max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'ms_ref_tpl'


##### 模板检测设置 #####
class TemplateCheckSetting(models.Model):
    spam_grade = models.IntegerField(default=1)
    min = models.DecimalField(max_digits=4, decimal_places=1)
    max = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        managed = False
        db_table = 'core_report_set'


##### 模板发送测试统计 #####
class TestSendTemplateLog(models.Model):
    user = models.ForeignKey(Customer, related_name='Customer03', db_index=True, null=False, blank=False)
    template = models.ForeignKey(SendTemplate, related_name='SendTemplate03', db_index=True, null=False, blank=False)
    test_time = models.IntegerField(u'发送时间')
    status = models.SmallIntegerField(u'状态', choices=TEST_STATUS, default='0')
    emails = models.CharField(u'邮箱', max_length=200, null=False, blank=False)
    ext = models.TextField(u'备注', null=True, blank=True)
    user_type = models.CharField(u'操作人员类型', max_length=20, null=False, blank=False, choices=TEST_USER_TYPE, default='users')

    class Meta:
        managed = False
        db_table = 'ms_send_template_log'

class ShareTemplte(models.Model):
    """  母账户单向的向子账户共享 模板
    子账户只能查看以及使用母账户模板，以及删除关系
    """
    template = models.ForeignKey(SendTemplate, null=False, blank=False, related_name="sub_share_template", on_delete=models.CASCADE)
    # 共享给目标用户id
    user = models.ForeignKey(Customer, related_name="sub_share_template_user", null=False, blank=False, db_index=True, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "ms_send_template_share"
        unique_together = (('template', "user"),)