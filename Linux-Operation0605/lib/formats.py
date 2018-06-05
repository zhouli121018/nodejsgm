import re

def safe_format(template, **kwargs):
    def replace(mo):
        name = mo.group('name')
        if name in kwargs:
            return unicode(kwargs[name])
        else:
            return mo.group()

    p = r'\{(?P<name>\w+)\}'
    return re.sub(p, replace, template)

def dict_compatibility(j, key, default=""):
    value = j[key] if key in j else default
    if value is None: value = default
    return value