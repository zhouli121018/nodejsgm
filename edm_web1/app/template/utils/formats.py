# coding=utf-8
from django.utils import formats
from django.utils.html import avoid_wrapping
from django.utils.translation import ungettext, ugettext
# from django.template.defaultfilters import filesizeformat as SysFilesizeformat, safe as makesafe

def filesizeformat(bytes):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    try:
        bytes = float(bytes)
    except (TypeError, ValueError, UnicodeDecodeError):
        value = ungettext("%(size)d byte", "%(size)d bytes", 0) % {'size': 0}
        return avoid_wrapping(value)

    filesize_number_format = lambda value: formats.number_format(round(value, 2), 2)

    KB = 1 << 10
    MB = 1 << 20
    GB = 1 << 30
    TB = 1 << 40
    PB = 1 << 50

    # if bytes < KB:
    #     value = ungettext("%(size)d byte", "%(size)d bytes", bytes) % {'size': bytes}
    if bytes < MB:
        value = ugettext("%s KB") % filesize_number_format(bytes / KB)
    elif bytes < GB:
        value = ugettext("%s MB") % filesize_number_format(bytes / MB)
    elif bytes < TB:
        value = ugettext("%s GB") % filesize_number_format(bytes / GB)
    elif bytes < PB:
        value = ugettext("%s TB") % filesize_number_format(bytes / TB)
    else:
        value = ugettext("%s PB") % filesize_number_format(bytes / PB)

    return avoid_wrapping(value)