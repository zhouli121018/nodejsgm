# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import posixpath
from urlparse import urlparse, urlunparse
from django.db import models
# from sorl.thumbnail import ImageField
from jsonfield import JSONField
from django.conf import settings
from lib.template import create_filepath
from app.mosaico.img import IsValidImage4Bytes


class Upload(models.Model):
    name = models.CharField(u'文件名', max_length=200, null=False, blank=False)
    # image = ImageField(upload_to="uploads")
    image = models.CharField(u"文件路径", max_length=100, null=False, blank=False, db_index=True,
                             help_text=u"文件的相对路径，路径：media/uploads/{user_id}/img/xxx.gif")
    user_id = models.IntegerField(u'客户ID')

    def __unicode__(self):
        return self.name

    @property
    def filepath(self):
        return os.path.join(settings.MEDIA_ROOT, self.image)

    @property
    def filesize(self):
        return os.path.getsize(self.filepath)

    @property
    def absurl(self):
        return "{}{}".format(settings.MEDIA_URL, self.image)

    @property
    def fileurl(self):
        parts = urlparse(self.absurl)
        if parts.netloc == '':
            newparts = list(parts)
            domain = settings.SITE_DOMAIN
            newparts[0] = 'http'
            newparts[1] = domain
            url = urlunparse(newparts)
        return url

    @staticmethod
    def imgsave(user_id, ifile):
        file_data = ifile.read()
        if not IsValidImage4Bytes(file_data):
            raise ValueError("File type is illegal.")
        file_name=ifile.name
        abs_path = "uploads/{}/img".format(user_id)
        make_path = os.path.join(settings.MEDIA_ROOT, abs_path)
        create_filepath(make_path)
        file_path = "{}/{}.{}".format(abs_path, uuid.uuid1(), file_name.split(".")[-1])
        real_path = os.path.join(settings.MEDIA_ROOT, file_path)
        with open(real_path, 'w') as f:
            f.write(file_data)
        upload = Upload(name=file_name, image=file_path, user_id=user_id)
        upload.save()
        return upload

    def to_json_data(self):
        url = self.fileurl
        data = {
            'size': self.filesize,
            'name': posixpath.basename(url),
            'originalName': posixpath.basename(self.name),
            'url': url,
            'thumbnailUrl': url,
            'deleteUrl': url,
            'deleteType': 'DELETE',
            'type': None,
        }
        # print data
        return data

    class Meta:
        managed = False
        db_table = 'mosaico_upload'


class Template(models.Model):
    # key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    html = models.TextField(verbose_name="HTML")
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    template_data = JSONField()
    meta_data = JSONField()
    user_id = models.IntegerField(u'客户ID')
    template_id = models.IntegerField(u'模板ID')

    def __unicode__(self):
        return "%s - %s" % (self.name, self.key)

    class Meta:
        managed = False
        db_table = 'mosaico_template'
        unique_together = (
            ('user_id', 'template_id'),
        )

