#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re


class Model(object):
    _type = ()

    def dump(self, d):
        return d

    def load(self, d):
        # True 和 False 不应视为 integer，所以不用 isinstance 验证类型
        if isinstance(self._type, tuple):
            assert type(d) in self._type
        else:
            assert type(d) == self._type
        self._validate(d)
        return self._load(d)

    def _validate(self, d):
        pass

    def _load(self, d):
        return d


class ObjectModel(Model):
    _type = dict

    def __init__(self, m, r):
        self._m = m
        self._r = r

    def dump(self, d):
        return {k: self._m[k].dump(d[k]) for k in d.keys()}

    def _validate(self, d):
        super(ObjectModel, self)._validate(d)
        assert set(d.keys()) >= self._r

    def _load(self, d):
        return {k: self._m[k].load(d[k]) for k in d.keys()}


class ArrayModel(Model):
    _type = list

    def __init__(self, m, a=1, b=None):
        self._m = m
        self._a = a
        self._b = b

    def dump(self, d):
        return [self._m.dump(i) for i in d]

    def _validate(self, d):
        super(ArrayModel, self)._validate(d)
        assert in_range(len(d), self._a, self._b)

    def _load(self, d):
        return [self._m.load(i) for i in d]


class StructureModel(Model):
    _type = list

    def __init__(self, m):
        self._m = m

    def dump(self, d):
        return [self._m[i].dump(d[i]) for i in xrange(len(d))]

    def _validate(self, d):
        super(StructureModel, self)._validate(d)
        assert len(d) == len(self._m)

    def _load(self, d):
        return [self._m[i].load(d[i]) for i in xrange(len(d))]


class NullModel(Model):
    _type = type(None)


class BooleanModel(Model):
    _type = bool


class IntegerModel(Model):
    _type = (int, long)


class NumberModel(Model):
    _type = (int, long, float)


class StringModel(Model):
    _type = unicode

    def dump(self, d):
        return unicode(d)


class RangeModel(IntegerModel):
    def __init__(self, a, b=None):
        self._a = a
        self._b = b

    def _validate(self, d):
        super(RangeModel, self)._validate(d)
        assert in_range(d, self._a, self._b)


class PatternModel(StringModel):
    def __init__(self, p):
        self._p = p

    def _validate(self, d):
        super(PatternModel, self)._validate(d)
        assert re.match(self._p, d) is not None


class DatetimeModel(StringModel):
    def _load(self, d):
        if len(d) == 26:
            return datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f')
        else:
            return datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')


def in_range(x, a, b):
    return (a is None or x >= a) and (b is None or x < b)


def model(s):
    if isinstance(s, list):
        if s[0] == 'object':
            return ObjectModel({i[0]: model(i[1]) for i in s[1:]},
                               {i[0] for i in s[1:] if len(i) <= 2 or i[2]})
        elif s[0] == 'array':
            return ArrayModel(model(s[1]), *s[2:])
        elif s[0] == 'structure':
            return StructureModel([model(i) for i in s[1:]])
        else:
            return _table[s[0]](*s[1:])
    else:
        return _table[s]


email_pattern = r'\A.+@(\w+[-.])*\w+\.\w+\Z'
ipv4_pattern = r'\A(((|[1-9]|1[0-9]|2[0-4])[0-9]|25[0-5])\.){3}((|[1-9]|1[0-9]|2[0-4])[0-9]|25[0-5])\Z'

_table = {
    'null': NullModel(),
    'boolean': BooleanModel(),
    'integer': IntegerModel(),
    'number': NumberModel(),
    'string': StringModel(),
    'range': RangeModel,
    'pattern': PatternModel,
    'datetime': DatetimeModel(),
    'email': PatternModel(email_pattern),
    'ipv4': PatternModel(ipv4_pattern)
}
