# -*- coding: utf-8 -*-
#

import re
import json
import urllib
import string
import random
import urlparse
from PIL import Image
from bs4 import BeautifulSoup

from django.conf import settings
from app.core.models import SysPicDomain
from app.mosaico.models import Upload

CHARS = string.letters

baseList = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
def changeBase(n,b):
    x,y = divmod(n,b)
    if x>0:
        return changeBase(x,b) + baseList[y]
    else:
        return baseList[y]

def changeToTenBase(s,b):
    sL = list(s)
    sL.reverse()
    result = 0
    for x in xrange(len(sL)):
        result = result + baseList.index(sL[x])*(b**x)
    return result

def get_random_string(start=1, end=10):
    return "".join([random.choice(CHARS) for i in range(random.randint(start, end))])

def get_mosaico_key(template_id):
    return "{:0>7}".format(changeBase(template_id, 62))

def get_template_id(key):
    return changeToTenBase(key, 62)

def get_size(size_txt):
    if size_txt == 'null':
        return None
    else:
        return int(size_txt)

def get_pic_domain():
    lists = SysPicDomain.objects.filter(isvalid=True)
    return random.choice(lists).domain if lists else random.choice(settings.TEMPLATE_PIC_URLS)

def get_site_domain():
    # site_domain = settings.SITE_DOMAIN
    site_domain = get_pic_domain()
    site_domain = site_domain.strip()
    if site_domain.startswith("http"):
        return site_domain
    return "http://{}".format(site_domain)

####################  退订替换 ####################################
# 退订链接 替换
def replace_unsubscribe_link(content):
    def _replace(matched):
        g = matched.group(1)
        if g:
            site_domain = get_site_domain()
            return ' href="{0}/template/ajax_unsubscribe_or_complaints/?mailist={1}MAILLIST_ID{2}&amp;recipents={1}RECIPIENTS{2}&amp;mode=0" '.format(
                site_domain, "{", "}"
            )
    return re.sub('(href="\[unsubscribe_link\]")', _replace, content)

# 查看模板链接 替换
def replace_show_link(template_id, content):
    def _replace(matched):
        g = matched.group(1)
        site_domain = get_site_domain()
        if g:
            return ' href="{0}/template/ajax_recipient_view_template/?recipents={1}RECIPIENTS{2}&amp;fullname={1}FULLNAME{2}&amp;send_id={1}SEND_ID{2}&amp;template_id={3}" '.format(
                site_domain, "{", "}", template_id
            )
    return re.sub('(href="\[show_link\]")', _replace, content)

####################  暂时不用 ####################################
# mosaico url 链接替换
def mosaico_replace_html_url(content):
    def _replace(matched):
        s1 = matched.group(1)
        s2 = matched.group(2)
        site_domain = get_site_domain()
        if s1 and s2:
            return 'href="{}/mosaico/img/?src={}'.format(site_domain, s2)
    return re.sub('(src="\/mosaico\/img\/\?src\=)(.*?)"', _replace, content)


def mosaico_replace_img(content):
    def _replace(marched):
        g = marched.group()
        g1, g2, g3, g4  = marched.group(1), marched.group(2), marched.group(3), marched.group(4)

        rs = urlparse.urlparse("{}{}".format(g2, g3))
        params = urlparse.parse_qs(rs.query)
        # {u'src': [u'http://192.168.1.24:8090/media/uploads/2369/img/da3e61a0-a344-11e7-bf13-005056a7d988.jpg'], u'params': [u'166,90"'], u'method': [u'cover']}
        method = params.get('method')[0]
        site_domain = get_site_domain()

        s = ' <img {} src="{}/mosaico/img/?src={}" {} > '.format(
            g1, site_domain, g3, g4
        )
        if method == "cover":
            m = re.search('\salt="(.*?)"\s', g)
            alt = m.group(1) if m else ""

            path = urlparse.urlsplit(params.get('src')[0]).path
            width, height = [get_size(p) for p in (params.get('params')[0]).split(',')]
            abspath = path.replace(settings.MEDIA_URL, "")

            upload=None
            for upload in Upload.objects.filter(image=abspath):
                if upload.absurl == path:
                    break
            src_width, src_height = width, height
            if upload:
                image = Image.open(upload.filepath)
                image.thumbnail((width, height), Image.ANTIALIAS)
                src_width, src_height = image.size
            s = ' <img src="{}/mosaico/img/?src={}" class="mobile-full" alt="{}" style="border:0px;display:block;vertical-align:top;width:{}px;height={}px;" vspace="0" hspace="0" border="0">'.format(
                site_domain, g3, alt, src_width, src_height
            )
        return s
    # <img class="mobile-full" alt="" style="border: 0px; display: block; vertical-align: top; width: 100%; height: auto;" src="http://192.168.1.24:8090/mosaico/img/?src=http%3A%2F%2F192.168.1.24%3A8090%2Fmedia%2Fuploads%2F2369%2Fimg%2Fda3e61a0-a344-11e7-bf13-005056a7d988.jpg&amp;method=cover&amp;params=166%2C90" width="166" vspace="0" hspace="0" height="90" border="0">
    # content = content.replace("\r", "").replace("\n", "").replace("  ", "")
    # print content
    return re.sub('\<img(.*?)src="(\/mosaico\/img\/\?src\=)(.*?)"(.*?)\>', _replace, content)

####################  链接替换 ####################################
# mosaico 图片链接替换
def mosaico_replace_html_src(content):
    def _replace(matched):
        g1, g2 = matched.group(1), matched.group(2)
        if g1 and g2:
            site_domain = get_site_domain()
            return 'src="{}/mosaico/img/?src={}"'.format(site_domain, g2)
    return re.sub('src="(\/mosaico\/img\/\?src\=)(.*?)"', _replace, content)

def mosaico_replace_html_static(content):
    def _replace(matched):
        g1, g2 = matched.group(1), matched.group(2)
        if g1 and g2:
            site_domain = get_site_domain()
            return 'src="{}{}{}"'.format(site_domain, g1, g2)
    return re.sub('src="(\/static\/mosaico\/templates\/)(.*?)"', _replace, content)

def mosaico_replace_html_p(content):
    def _replace(marched):
        g0, g1, g2, g3 = marched.group(1), marched.group(2), marched.group(3), marched.group(4)
        g0 = g0 if g0.endswith(";") else "{};".format(g0)
        return '<p data-mce-style="{0}" {1} style="{2} {0}" {3}>'.format(g0, g1, g2, g3)
    return re.sub(r'<p data-mce-style="(.*?)"(.*?)style="(.*?)"(.*?)>', _replace, content)

def mosaico_replace_td_img(content):
    def _replace(marched):
        g0, g1, g2, g3, g4, g5, g6, g7, g8  = marched.group(1), marched.group(2), marched.group(3), marched.group(4), marched.group(5), marched.group(6), marched.group(7), marched.group(8), marched.group(9)
        g3 = g3.strip()
        g3 = g3 if g3.endswith(";") else "{};".format(g3)

        # 图片链接
        rs = urlparse.urlparse("{}{}".format(g6, g7))
        params = urlparse.parse_qs(rs.query)
        # {u'src': [u'http://192.168.1.24:8090/media/uploads/2369/img/da3e61a0-a344-11e7-bf13-005056a7d988.jpg'], u'params': [u'166,90"'], u'method': [u'cover']}
        method = params.get('method')[0]
        site_domain = get_site_domain()

        s = '<tr>{0}<td {1} style="{2} display: table-cell;text-align: center;vertical-align: middle;" {3}> {4} <img {5} src="{6}/mosaico/img/?src={7}"{8}>'.format(
            g0, g1, g2, g3, g4, g5, site_domain, g7, g8
        )
        if method == "cover":
            g_img = '<img{0}src="{1}{2}"{3}>'.format(g5, g6, g7, g8)
            m = re.search('\salt="(.*?)"\s', g_img)
            alt = m.group(1) if m else ""

            path = urlparse.urlsplit(params.get('src')[0]).path
            width, height = [get_size(p) for p in (params.get('params')[0]).split(',')]
            abspath = path.replace(settings.MEDIA_URL, "")

            upload=None
            for upload in Upload.objects.filter(image=abspath):
                if upload.absurl == path:
                    break
            src_width, src_height = width, height
            if upload:
                image = Image.open(upload.filepath)
                image.thumbnail((width, height), Image.ANTIALIAS)
                src_width, src_height = image.size
            s = '''<tr>{0}<td {1} style="{2} display: table-cell;text-align: center;vertical-align: middle; height: {10}px;" {3}> {4}
                <img src="{5}/mosaico/img/?src={6}" class="mobile-full" alt="{7}" style="border:0px;display:block;vertical-align:top;width:{8}px;height={9}px;" vspace="0" hspace="0" border="0">
            '''.format(
                g0, g1, g2, g3, g4, site_domain, g7, alt, src_width, src_height, height
            )
        return s
    return re.sub(r'<tr>(.*?)<td(.*?)style="(.*?)"(.*?)>(.*?)<img(.*?)src="(\/mosaico\/img\/\?src\=)(.*?)"(.*?)>', _replace, content)

def soup_find(soup, html):
    tags = soup.findAll("table", attrs={"class": "vb-content"})
    for item in tags:
        for iitem in item.children:
            for iiitem in iitem.children:
                iiitem = unicode(iiitem)
                _iiitem = mosaico_replace_td_img(iiitem)
                html = html.replace(iiitem, _iiitem)
    return html

def replace_template(template_id, html):
    soup1 = BeautifulSoup(html, 'html5lib')
    html = unicode(soup1)
    html = html.replace("\r", "").replace("\n", "").replace("  ", "")
    soup = BeautifulSoup(html, 'html5lib')
    html = soup_find(soup, html)

    html = replace_unsubscribe_link(html)
    html = replace_show_link(template_id, html)
    html = mosaico_replace_html_src(html)
    html = mosaico_replace_html_p(html)
    html = mosaico_replace_html_static(html)
    return html


TEXT_CONTENT = u'''如果邮件内容无法正常显示请以超文本格式显示HTML邮件！\n
        （If the content of the message does not display properly, please display the HTML message in hypertext format!）'''

MOSAICO_AUTH_KEY = "oDerVO!0Dfh6789qAk5J#5tem12jeRJd"

class Tedc15Settings(object):
    TEMPLATE_DATA = {
        'bodyWidth': '660',
        'gutterWidth': '20',
        'mainBlocks': {'blocks': [], 'type': 'blocks'},
        'sansFace': "Frutiger, 'Frutiger Linotype', 'Helvetica Neue', Helvetica, Arial, sans-serif",
        'serifFace': "Rawlinson, Georgia, 'Times', 'Times New Roman', serif",
        'theme': {'bodyTheme': None, 'type': 'theme'},
        'type': 'template'
    }
    DEFAULT_HTML = """
    <!DOCTYPE html>
    <html>
        <head></head>
        <body style="background-color: #202020; color: #FFFFFF; margin: 0;" text="#FFFFFF"><center></center></body>
    </html>
    """

class VersafixSettings(object):
    TEMPLATE_DATA = {
        'customStyle': False,
        'footerBlock': {'backgroundColor': None,
                        'customStyle': False,
                        'disiscrivitiText': u'请点击这里退订',
                        'id': 'ko_footerBlock_2',
                        'linkStyle': {'color': None,
                                      'decoration': None,
                                      'face': None,
                                      'size': None,
                                      'type': 'linkStyle'},
                        'longText': u"如果您不想再收到此类邮件,",
                        'longTextStyle': {'color': None,
                                          'face': None,
                                          'linksColor': None,
                                          'size': None,
                                          'type': 'longTextStyle'},
                        'type': 'footerBlock'},
        'mainBlocks': {'blocks': [], 'type': 'blocks'},
        'preheaderBlock': {'backgroundColor': None,
                           'customStyle': False,
                           'id': 'ko_preheaderBlock_1',
                           'linkStyle': {'color': None,
                                         'decoration': None,
                                         'face': None,
                                         'size': None,
                                         'type': 'linkStyle'},
                           'longTextStyle': {'color': None,
                                             'face': None,
                                             'linksColor': None,
                                             'size': None,
                                             'type': 'longTextStyle'},
                           'preheaderLinkOption': '[unsubscribe_link]',
                           'preheaderText': '',
                           'type': 'preheaderBlock',
                           'unsubscribeText': u'退订',
                           'webversionText': u'邮件无法显示请点击这里'},
        'preheaderVisible': True,

        'sponsor': {'alt': 'sponsor',
                    'src': 'http://{}/static/mosaico/templates/versafix-1/img/sponsor.gif'.format(settings.SITE_DOMAIN),
                    'type': 'sponsor',
                    'url': '',
                    'visible': False},

        'theme': {'contentTheme': {'backgroundColor': '#ffffff',
                                   'bigButtonStyle': {'buttonColor': '#bfbfbf',
                                                      'color': '#3f3f3f',
                                                      'face': 'Arial, Helvetica, sans-serif',
                                                      'radius': '4',
                                                      'size': '22',
                                                      'type': 'buttonStyle'},
                                   'bigTitleStyle': {'align': 'center',
                                                     'color': '#3f3f3f',
                                                     'face': 'Arial, Helvetica, sans-serif',
                                                     'size': '22',
                                                     'type': 'bigTitleStyle'},
                                   'buttonStyle': {'buttonColor': '#bfbfbf',
                                                   'color': '#3f3f3f',
                                                   'face': 'Arial, Helvetica, sans-serif',
                                                   'radius': '4',
                                                   'size': '13',
                                                   'type': 'buttonStyle'},
                                   'externalBackgroundColor': '#ffffff',
                                   'externalTextStyle': {'color': '#f3f3f3',
                                                         'face': 'Arial, Helvetica, sans-serif',
                                                         'size': '18',
                                                         'type': 'textStyle'},
                                   'hrStyle': {'color': '#3f3f3f',
                                               'hrHeight': '1',
                                               'hrWidth': '100',
                                               'type': 'hrStyle'},
                                   'longTextStyle': {'color': '#3f3f3f',
                                                     'face': 'Arial, Helvetica, sans-serif',
                                                     'linksColor': '#3f3f3f',
                                                     'size': '13',
                                                     'type': 'longTextStyle'},
                                   'titleTextStyle': {'color': '#3f3f3f',
                                                      'face': 'Arial, Helvetica, sans-serif',
                                                      'size': '18',
                                                      'type': 'textStyle'},
                                   'type': 'contentTheme'},
                  'frameTheme': {'backgroundColor': '#f1f1f1',
                                 'linkStyle': {'color': '#0070c0',
                                               'decoration': 'underline',
                                               'face': 'Arial, Helvetica, sans-serif',
                                               'size': '13',
                                               'type': 'linkStyle'},
                                 'longTextStyle': {'color': '#919191',
                                                   'face': 'Arial, Helvetica, sans-serif',
                                                   'linksColor': '#0070c0',
                                                   'size': '13',
                                                   'type': 'longTextStyle'},
                                 'type': 'frameTheme'},
                  'type': 'theme'},
        'titleText': 'TITLE',
        'type': 'template'
    }

    DEFAULT_HTML = u"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"><head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <meta name="viewport" content="initial-scale=1.0">
      <meta name="format-detection" content="telephone=no">
      <title>TITLE</title>

      <style type="text/css">
        body{ Margin: 0; padding: 0; }
        img{ border: 0px; display: block; }

        .socialLinks{ font-size: 6px; }
        .socialLinks a{
          display: inline-block;
        }
        .socialIcon{
          display: inline-block;
          vertical-align: top;
          padding-bottom: 0px;
          border-radius: 100%;
        }
        .oldwebkit{ max-width: 570px; }
        td.vb-outer{ padding-left: 9px; padding-right: 9px; }
        table.vb-container, table.vb-row, table.vb-content{
          border-collapse: separate;
        }
        table.vb-row{
          border-spacing: 9px;
        }
        table.vb-row.halfpad{
          border-spacing: 0;
          padding-left: 9px;
          padding-right: 9px;
        }
        table.vb-row.fullwidth{
          border-spacing: 0;
          padding: 0;
        }
        table.vb-container{
          padding-left: 18px;
          padding-right: 18px;
        }
        table.vb-container.fullpad{
          border-spacing: 18px;
          padding-left: 0;
          padding-right: 0;
        }
        table.vb-container.halfpad{
          border-spacing: 9px;
          padding-left: 9px;
          padding-right: 9px;
        }
        table.vb-container.fullwidth{
          padding-left: 0;
          padding-right: 0;
        }
      </style>
      <style type="text/css">
        /* yahoo, hotmail */
        .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div{ line-height: 100%; }
        .yshortcuts a{ border-bottom: none !important; }
        .vb-outer{ min-width: 0 !important; }
        .RMsgBdy, .ExternalClass{
          width: 100%;
          background-color: #3f3f3f;
          background-color: #3f3f3f}

        /* outlook */
        table{ mso-table-rspace: 0pt; mso-table-lspace: 0pt; }
        #outlook a{ padding: 0; }
        img{ outline: none; text-decoration: none; border: none; -ms-interpolation-mode: bicubic; }
        a img{ border: none; }

        @media screen and (max-device-width: 600px), screen and (max-width: 600px) {
          table.vb-container, table.vb-row{
            width: 95% !important;
          }

          .mobile-hide{ display: none !important; }
          .mobile-textcenter{ text-align: center !important; }

          .mobile-full{
            float: none !important;
            width: 100% !important;
            max-width: none !important;
            padding-right: 0 !important;
            padding-left: 0 !important;
          }
          img.mobile-full{
            width: 100% !important;
            max-width: none !important;
            height: auto !important;
          }
        }
      </style>
      <style type="text/css">

        #ko_footerBlock_2 .links-color a, #ko_footerBlock_2 .links-color a:link, #ko_footerBlock_2 .links-color a:visited, #ko_footerBlock_2 .links-color a:hover{
          color: #cccccc;
          color: #cccccc;
          text-decoration: underline
        }
         #ko_footerBlock_2 .long-text p{ Margin: 1em 0px }  #ko_footerBlock_2 .long-text p:last-child{ Margin-bottom: 0px }  #ko_footerBlock_2 .long-text p:first-child{ Margin-top: 0px } </style>
    </head>
    <body style="Margin: 0; padding: 0; background-color: #3f3f3f; color: #919191;" vlink="#cccccc" text="#919191" bgcolor="#3f3f3f" alink="#cccccc">

      <center>

      <!-- preheaderBlock -->


      <table class="vb-outer" style="background-color: #3f3f3f;" id="ko_preheaderBlock_1" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#3f3f3f">
        <tbody><tr>
          <td class="vb-outer" style="padding-left: 9px; padding-right: 9px; background-color: #3f3f3f;" valign="top" bgcolor="#3f3f3f" align="center">
            <div style="display: none; font-size: 1px; color: #333333; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;"></div>

    <!--[if (gte mso 9)|(lte ie 8)]><table align="center" border="0" cellspacing="0" cellpadding="0" width="570"><tr><td align="center" valign="top"><![endif]-->
            <div class="oldwebkit" style="max-width: 570px;">
            <table class="vb-row halfpad" style="border-collapse: separate; border-spacing: 0; padding-left: 9px; padding-right: 9px; width: 100%; max-width: 570px; background-color: #3f3f3f;" width="570" cellspacing="0" cellpadding="0" border="0" bgcolor="#3f3f3f">
              <tbody><tr>
                <td style="font-size: 0; background-color: #3f3f3f;" valign="top" bgcolor="#3f3f3f" align="center">

    <!--[if (gte mso 9)|(lte ie 8)]><table align="center" border="0" cellspacing="0" cellpadding="0" width="552"><tr><![endif]-->
    <!--[if (gte mso 9)|(lte ie 8)]><td align="left" valign="top" width="276"><![endif]-->
    <div style="display: inline-block; max-width: 276px; vertical-align: top; width: 100%;" class="mobile-full">
                        <table class="vb-content" style="border-collapse: separate; width: 100%;" width="276" cellspacing="9" cellpadding="0" border="0" align="left">
                          <tbody><tr>
                            <td style="font-weight: normal; text-align: left; font-size: 13px; font-family: Arial, Helvetica, sans-serif; color: #ffffff;" width="100%" valign="top" align="left">
                              <a style="text-decoration: underline; color: #ffffff;" target="_new" href="{unsubscribe_link}">取消订阅</a>

                            </td>
                          </tr>
                        </tbody></table>
    </div><!--[if (gte mso 9)|(lte ie 8)]>
    </td><td align="left" valign="top" width="276">
    <![endif]--><div style="display: inline-block; max-width: 276px; vertical-align: top; width: 100%;" class="mobile-full mobile-hide">

                        <table class="vb-content" style="border-collapse: separate; width: 100%; text-align: right;" width="276" cellspacing="9" cellpadding="0" border="0" align="left">
                          <tbody><tr>
                            <td style="font-weight: normal; font-size: 13px; font-family: Arial, Helvetica, sans-serif; color: #ffffff;" width="100%" valign="top">
                          <span style="color: #ffffff; text-decoration: underline;">
                              <a href="{show_link}" style="text-decoration: underline; color: #ffffff;" target="_new">邮件无法显示请点击这里</a>
                             </span>
                           </td>
                          </tr>
                        </tbody></table>

    </div><!--[if (gte mso 9)|(lte ie 8)]>
    </td></tr></table><![endif]-->

                </td>
              </tr>
            </tbody></table>
            </div>
    <!--[if (gte mso 9)|(lte ie 8)]></td></tr></table><![endif]-->
          </td>
        </tr>
      </tbody></table>


      <!-- /preheaderBlock -->



      <!-- footerBlock -->
      <table style="background-color: #3f3f3f;" id="ko_footerBlock_2" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#3f3f3f">
        <tbody><tr>
          <td style="background-color: #3f3f3f;" valign="top" bgcolor="#3f3f3f" align="center">

    <!--[if (gte mso 9)|(lte ie 8)]><table align="center" border="0" cellspacing="0" cellpadding="0" width="570"><tr><td align="center" valign="top"><![endif]-->
            <div class="oldwebkit" style="max-width: 570px;">
            <table style="border-collapse: separate; border-spacing: 9px; padding-left: 9px; padding-right: 9px; width: 100%; max-width: 570px;" class="vb-container halfpad" width="570" cellspacing="9" cellpadding="0" border="0" align="center">
              <tbody><tr>
                <td class="long-text links-color" style="text-align: center; font-size: 13px; color: #919191; font-weight: normal; text-align: center; font-family: Arial, Helvetica, sans-serif;"><p style="Margin: 1em 0px; Margin-bottom: 0px; Margin-top: 0px;">Email sent to <a href="mailto:{mail}" style="color: #cccccc; color: #cccccc; text-decoration: underline;">{mail}</a></p></td>
              </tr>
              <tr>
                <td style="text-align: center;">
                  <a href="{unsubscribe_link}" style="text-decoration: underline; color: #ffffff; text-align: center; font-size: 13px; font-weight: normal; font-family: Arial, Helvetica, sans-serif;" target="_new"><span>Unsubscribe</span></a>
                </td>
              </tr>

            </tbody></table>
            </div>
    <!--[if (gte mso 9)|(lte ie 8)]></td></tr></table><![endif]-->
          </td>
        </tr>
      </tbody></table>
      <!-- /footerBlock -->

      </center>

    </body></html>
    """

    TEMPLATE_DATA_EN = {
        'customStyle': False,
        'footerBlock': {'backgroundColor': None,
                        'customStyle': False,
                        'disiscrivitiText': u'Unsubscribe',
                        'id': 'ko_footerBlock_2',
                        'linkStyle': {'color': None,
                                      'decoration': None,
                                      'face': None,
                                      'size': None,
                                      'type': 'linkStyle'},
                        'longText':None,
                        'longTextStyle': {'color': None,
                                          'face': None,
                                          'linksColor': None,
                                          'size': None,
                                          'type': 'longTextStyle'},
                        'type': 'footerBlock'},
        'mainBlocks': {'blocks': [], 'type': 'blocks'},
        'preheaderBlock': {'backgroundColor': None,
                           'customStyle': False,
                           'id': 'ko_preheaderBlock_1',
                           'linkStyle': {'color': None,
                                         'decoration': None,
                                         'face': None,
                                         'size': None,
                                         'type': 'linkStyle'},
                           'longTextStyle': {'color': None,
                                             'face': None,
                                             'linksColor': None,
                                             'size': None,
                                             'type': 'longTextStyle'},
                           'preheaderLinkOption': '[unsubscribe_link]',
                           'preheaderText': '',
                           'type': 'preheaderBlock',
                           'unsubscribeText': 'Unsubscribe',
                           'webversionText': 'View in your browser'},
        'preheaderVisible': True,
        'sponsor': {'alt': 'sponsor',
                    'src': 'http://{}/static/mosaico/templates/versafix-1/img/sponsor.gif'.format(settings.SITE_DOMAIN),
                    'type': 'sponsor',
                    'url': '',
                    'visible': True},
        'theme': {'contentTheme': {'backgroundColor': '#ffffff',
                                   'bigButtonStyle': {'buttonColor': '#bfbfbf',
                                                      'color': '#3f3f3f',
                                                      'face': 'Arial, Helvetica, sans-serif',
                                                      'radius': '4',
                                                      'size': '22',
                                                      'type': 'buttonStyle'},
                                   'bigTitleStyle': {'align': 'center',
                                                     'color': '#3f3f3f',
                                                     'face': 'Arial, Helvetica, sans-serif',
                                                     'size': '22',
                                                     'type': 'bigTitleStyle'},
                                   'buttonStyle': {'buttonColor': '#bfbfbf',
                                                   'color': '#3f3f3f',
                                                   'face': 'Arial, Helvetica, sans-serif',
                                                   'radius': '4',
                                                   'size': '13',
                                                   'type': 'buttonStyle'},
                                   'externalBackgroundColor': '#ffffff',
                                   'externalTextStyle': {'color': '#f3f3f3',
                                                         'face': 'Arial, Helvetica, sans-serif',
                                                         'size': '18',
                                                         'type': 'textStyle'},
                                   'hrStyle': {'color': '#3f3f3f',
                                               'hrHeight': '1',
                                               'hrWidth': '100',
                                               'type': 'hrStyle'},
                                   'longTextStyle': {'color': '#3f3f3f',
                                                     'face': 'Arial, Helvetica, sans-serif',
                                                     'linksColor': '#3f3f3f',
                                                     'size': '13',
                                                     'type': 'longTextStyle'},
                                   'titleTextStyle': {'color': '#3f3f3f',
                                                      'face': 'Arial, Helvetica, sans-serif',
                                                      'size': '18',
                                                      'type': 'textStyle'},
                                   'type': 'contentTheme'},
                  'frameTheme': {'backgroundColor': '#f1f1f1',
                                 'linkStyle': {'color': '##0070c0',
                                               'decoration': 'underline',
                                               'face': 'Arial, Helvetica, sans-serif',
                                               'size': '13',
                                               'type': 'linkStyle'},
                                 'longTextStyle': {'color': '#919191',
                                                   'face': 'Arial, Helvetica, sans-serif',
                                                   'linksColor': '#0070c0',
                                                   'size': '13',
                                                   'type': 'longTextStyle'},
                                 'type': 'frameTheme'},
                  'type': 'theme'},
        'titleText': 'TITLE',
        'type': 'template'
    }

    DEFAULT_HTML_EN = u"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"><head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <meta name="viewport" content="initial-scale=1.0">
      <meta name="format-detection" content="telephone=no">
      <title>TITLE</title>

      <style type="text/css">
        body{ Margin: 0; padding: 0; }
        img{ border: 0px; display: block; }

        .socialLinks{ font-size: 6px; }
        .socialLinks a{
          display: inline-block;
        }
        .socialIcon{
          display: inline-block;
          vertical-align: top;
          padding-bottom: 0px;
          border-radius: 100%;
        }
        .oldwebkit{ max-width: 570px; }
        td.vb-outer{ padding-left: 9px; padding-right: 9px; }
        table.vb-container, table.vb-row, table.vb-content{
          border-collapse: separate;
        }
        table.vb-row{
          border-spacing: 9px;
        }
        table.vb-row.halfpad{
          border-spacing: 0;
          padding-left: 9px;
          padding-right: 9px;
        }
        table.vb-row.fullwidth{
          border-spacing: 0;
          padding: 0;
        }
        table.vb-container{
          padding-left: 18px;
          padding-right: 18px;
        }
        table.vb-container.fullpad{
          border-spacing: 18px;
          padding-left: 0;
          padding-right: 0;
        }
        table.vb-container.halfpad{
          border-spacing: 9px;
          padding-left: 9px;
          padding-right: 9px;
        }
        table.vb-container.fullwidth{
          padding-left: 0;
          padding-right: 0;
        }
      </style>
      <style type="text/css">
        /* yahoo, hotmail */
        .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div{ line-height: 100%; }
        .yshortcuts a{ border-bottom: none !important; }
        .vb-outer{ min-width: 0 !important; }
        .RMsgBdy, .ExternalClass{
          width: 100%;
          background-color: #3f3f3f;
          background-color: #3f3f3f}

        /* outlook */
        table{ mso-table-rspace: 0pt; mso-table-lspace: 0pt; }
        #outlook a{ padding: 0; }
        img{ outline: none; text-decoration: none; border: none; -ms-interpolation-mode: bicubic; }
        a img{ border: none; }

        @media screen and (max-device-width: 600px), screen and (max-width: 600px) {
          table.vb-container, table.vb-row{
            width: 95% !important;
          }

          .mobile-hide{ display: none !important; }
          .mobile-textcenter{ text-align: center !important; }

          .mobile-full{
            float: none !important;
            width: 100% !important;
            max-width: none !important;
            padding-right: 0 !important;
            padding-left: 0 !important;
          }
          img.mobile-full{
            width: 100% !important;
            max-width: none !important;
            height: auto !important;
          }
        }
      </style>
      <style type="text/css">

        #ko_footerBlock_2 .links-color a, #ko_footerBlock_2 .links-color a:link, #ko_footerBlock_2 .links-color a:visited, #ko_footerBlock_2 .links-color a:hover{
          color: #cccccc;
          color: #cccccc;
          text-decoration: underline
        }
         #ko_footerBlock_2 .long-text p{ Margin: 1em 0px }  #ko_footerBlock_2 .long-text p:last-child{ Margin-bottom: 0px }  #ko_footerBlock_2 .long-text p:first-child{ Margin-top: 0px } </style>
    </head>
    <body style="Margin: 0; padding: 0; background-color: #3f3f3f; color: #919191;" vlink="#cccccc" text="#919191" bgcolor="#3f3f3f" alink="#cccccc">

      <center>

      <!-- preheaderBlock -->


      <table class="vb-outer" style="background-color: #3f3f3f;" id="ko_preheaderBlock_1" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#3f3f3f">
        <tbody><tr>
          <td class="vb-outer" style="padding-left: 9px; padding-right: 9px; background-color: #3f3f3f;" valign="top" bgcolor="#3f3f3f" align="center">
            <div style="display: none; font-size: 1px; color: #333333; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;"></div>

    <!--[if (gte mso 9)|(lte ie 8)]><table align="center" border="0" cellspacing="0" cellpadding="0" width="570"><tr><td align="center" valign="top"><![endif]-->
            <div class="oldwebkit" style="max-width: 570px;">
            <table class="vb-row halfpad" style="border-collapse: separate; border-spacing: 0; padding-left: 9px; padding-right: 9px; width: 100%; max-width: 570px; background-color: #3f3f3f;" width="570" cellspacing="0" cellpadding="0" border="0" bgcolor="#3f3f3f">
              <tbody><tr>
                <td style="font-size: 0; background-color: #3f3f3f;" valign="top" bgcolor="#3f3f3f" align="center">

    <!--[if (gte mso 9)|(lte ie 8)]><table align="center" border="0" cellspacing="0" cellpadding="0" width="552"><tr><![endif]-->
    <!--[if (gte mso 9)|(lte ie 8)]><td align="left" valign="top" width="276"><![endif]-->
    <div style="display: inline-block; max-width: 276px; vertical-align: top; width: 100%;" class="mobile-full">
                        <table class="vb-content" style="border-collapse: separate; width: 100%;" width="276" cellspacing="9" cellpadding="0" border="0" align="left">
                          <tbody><tr>
                            <td style="font-weight: normal; text-align: left; font-size: 13px; font-family: Arial, Helvetica, sans-serif; color: #ffffff;" width="100%" valign="top" align="left">
                              <a style="text-decoration: underline; color: #ffffff;" target="_new" href="[unsubscribe_link]">Unsubscribe</a>

                            </td>
                          </tr>
                        </tbody></table>
    </div><!--[if (gte mso 9)|(lte ie 8)]>
    </td><td align="left" valign="top" width="276">
    <![endif]--><div style="display: inline-block; max-width: 276px; vertical-align: top; width: 100%;" class="mobile-full mobile-hide">

                        <table class="vb-content" style="border-collapse: separate; width: 100%; text-align: right;" width="276" cellspacing="9" cellpadding="0" border="0" align="left">
                          <tbody><tr>
                            <td style="font-weight: normal; font-size: 13px; font-family: Arial, Helvetica, sans-serif; color: #ffffff;" width="100%" valign="top">
                          <span style="color: #ffffff; text-decoration: underline;">
                              <a href=[show_link]" style="text-decoration: underline; color: #ffffff;" target="_new">View in your browser</a>
                             </span>
                           </td>
                          </tr>
                        </tbody></table>

    </div><!--[if (gte mso 9)|(lte ie 8)]>
    </td></tr></table><![endif]-->

                </td>
              </tr>
            </tbody></table>
            </div>
    <!--[if (gte mso 9)|(lte ie 8)]></td></tr></table><![endif]-->
          </td>
        </tr>
      </tbody></table>


      <!-- /preheaderBlock -->



      <!-- footerBlock -->
      <table style="background-color: #3f3f3f;" id="ko_footerBlock_2" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#3f3f3f">
        <tbody><tr>
          <td style="background-color: #3f3f3f;" valign="top" bgcolor="#3f3f3f" align="center">

    <!--[if (gte mso 9)|(lte ie 8)]><table align="center" border="0" cellspacing="0" cellpadding="0" width="570"><tr><td align="center" valign="top"><![endif]-->
            <div class="oldwebkit" style="max-width: 570px;">
            <table style="border-collapse: separate; border-spacing: 9px; padding-left: 9px; padding-right: 9px; width: 100%; max-width: 570px;" class="vb-container halfpad" width="570" cellspacing="9" cellpadding="0" border="0" align="center">
              <tbody><tr>
                <td class="long-text links-color" style="text-align: center; font-size: 13px; color: #919191; font-weight: normal; text-align: center; font-family: Arial, Helvetica, sans-serif;"><p style="Margin: 1em 0px; Margin-bottom: 0px; Margin-top: 0px;">Email sent to <a href="mailto:{mail}" style="color: #cccccc; color: #cccccc; text-decoration: underline;">{mail}</a></p></td>
              </tr>
              <tr>
                <td style="text-align: center;">
                  <a href="[unsubscribe_link]" style="text-decoration: underline; color: #ffffff; text-align: center; font-size: 13px; font-weight: normal; font-family: Arial, Helvetica, sans-serif;" target="_new"><span>Unsubscribe</span></a>
                </td>
              </tr>
              <tr style="text-align: center;">
                <td align="center">
                    <a style=";" target="_new" href=""><img src="http://192.168.1.24:9090/static/mosaico/templates/versafix-1/img/sponsor.gif" alt="sponsor" style="border: 0px; Margin: auto; display: inline;" vspace="0" hspace="0" border="0"></a>
                </td>
              </tr>
            </tbody></table>
            </div>
    <!--[if (gte mso 9)|(lte ie 8)]></td></tr></table><![endif]-->
          </td>
        </tr>
      </tbody></table>
      <!-- /footerBlock -->

      </center>

    </body></html>
    """

