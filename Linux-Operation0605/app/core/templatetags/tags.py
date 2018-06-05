# coding=utf-8
import datetime
from django import template
from app.core.models import Domain
from app.utils.domain_session import get_domainid_bysession

register = template.Library()


@register.filter
def int2datetime(t):
    try:
        return datetime.datetime.fromtimestamp(float(t)).strftime("%Y-%m-%d %H:%M:%S") if t else '-'
    except:
        return t

@register.filter
def float2percent(t):
    return '%.2f' % t if isinstance(t, float) else '-'

@register.filter
def list_sum(list, key):
    return sum([l.get(key, 0) for l in list])

@register.filter
def preview_check(filname):
    # allow_suffix = ( 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff', 'xbm', 'xpm',
    # 'doc', 'docx', 'dot', 'dotx',
    #                  'ppt', 'pptx', 'pps', 'ppsx', 'pot', 'potx',
    #                  'xls', 'xlsx', 'xlt', 'xltx'
    # )
    allow_suffix = ( 'jpg', 'jpeg', 'png', 'gif', 'bmp')
    suffix = filname.split('.')[-1]
    suffix = suffix.lower()
    return suffix in allow_suffix

@register.filter
def smooth_timedelta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs > 86400: # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} 天".format(int(days))
        secs = secs - days*86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} 小时".format(int(hrs))
        secs = secs - hrs*3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} 分钟".format(int(mins))
        secs = secs - mins*60

    if secs > 0:
        timetot += " {} 秒".format(int(secs))
    return timetot

@register.inclusion_tag('switch_domain.html')
def switch_domain(request):
    domain_list = Domain.objects.filter(disabled='-1')
    domain_id = get_domainid_bysession(request)
    return {
        'domain_list': domain_list,
        'domain_id': domain_id
    }
