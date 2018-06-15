# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
from struct import *
import string

def ip2string(ip):
    a = (ip & 0xff000000) >> 24
    b = (ip & 0x00ff0000) >> 16
    c = (ip & 0x0000ff00) >> 8
    d = ip & 0x000000ff
    return "%d.%d.%d.%d" % (a, b, c, d)

def string2ip(str):
    ss = string.split(str, '.');
    ip = 0L
    for s in ss: ip = (ip << 8) + string.atoi(s)
    return ip;

### 解码 ###
def decode_str(s):
    try:
        return s.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return s.decode('gb18030')
        except UnicodeDecodeError:
            return s.decode('utf-8', 'replace')

### 编码 ###
def encode_str(s):
    try:
        return s.encode('utf-8')
    except UnicodeEncodeError:
        try:
            return s.encode('gb18030')
        except UnicodeEncodeError:
            return s.encode('utf-8', 'replace')

def decode_encode_str(s):
    try:
        return decode_str(s)
    except:
        return encode_str(s).decode('utf-8')

class IpLocater:
    def __init__(self, ipdb_file=''):
        if not ipdb_file:
            ipdb_file = os.path.join(os.path.realpath(os.path.split(__file__)[0]), 'qqwry.dat')
        self.ipdb = open(ipdb_file, "rb")
        # get index address
        str = self.ipdb.read(8)
        (self.first_index, self.last_index) = unpack('II', str)
        self.index_count = (self.last_index - self.first_index) / 7 + 1

    def getString(self, offset=0):
        if offset:
            self.ipdb.seek(offset)
        str = ""
        ch = self.ipdb.read(1)
        (byte,) = unpack('B', ch)
        while byte != 0:
            str = str + ch
            ch = self.ipdb.read(1)
            (byte,) = unpack('B', ch)
        return str

    def getLong3(self, offset=0):
        if offset:
            self.ipdb.seek(offset)
        str = self.ipdb.read(3)
        (a, b) = unpack('HB', str)
        return (b << 16) + a

    def getAreaAddr(self, offset=0):
        if offset:
            self.ipdb.seek(offset)
        str = self.ipdb.read(1)
        (byte,) = unpack('B', str)
        if byte == 0x01 or byte == 0x02:
            p = self.getLong3()
            if p:
                return self.getString(p)
            else:
                return ""
        else:
            return self.getString(offset)

    def getAddr(self, offset, ip=0):
        self.ipdb.seek(offset + 4)

        countryAddr = ""
        areaAddr = ""
        str = self.ipdb.read(1)
        (byte,) = unpack('B', str)
        if byte == 0x01:
            countryOffset = self.getLong3()
            self.ipdb.seek(countryOffset)
            str = self.ipdb.read(1)
            (b,) = unpack('B', str)
            if b == 0x02:
                countryAddr = self.getString(self.getLong3())
                self.ipdb.seek(countryOffset + 4)
            else:
                countryAddr = self.getString(countryOffset)
            areaAddr = self.getAreaAddr()
        elif byte == 0x02:
            countryAddr = self.getString(self.getLong3())
            areaAddr = self.getAreaAddr(offset + 8)
        else:
            countryAddr = self.getString(offset + 4)
            areaAddr = self.getAreaAddr()
        return decode_encode_str(countryAddr), decode_encode_str(areaAddr)

        return unicode(countryAddr, 'gb2312'), unicode(areaAddr, 'gb2312')

        return countryAddr.decode('gb2312') + "/" + areaAddr.decode('gb2312')

    def output(self, first, last):
        if last > self.index_count:
            last = self.index_count
        for index in range(first, last):
            offset = self.first_index + index * 7
            self.ipdb.seek(offset)
            buf = self.ipdb.read(7)
            (ip, of1, of2) = unpack("IHB", buf)
            a, c = self.getAddr(of1 + (of2 << 16))
            # print "%s - %s - %s" % (ip, a, c)

    def find(self, ip, left, right):
        if right - left == 1:
            return left
        else:
            middle = ( left + right ) / 2
            offset = self.first_index + middle * 7
            self.ipdb.seek(offset)
            buf = self.ipdb.read(4)
            (new_ip,) = unpack("I", buf)
            if ip <= new_ip:
                return self.find(ip, left, middle)
            else:
                return self.find(ip, middle, right)

    def getIpAddr(self, ip):
        ip = string2ip(ip)
        index = self.find(ip, 0, self.index_count - 1)
        ioffset = self.first_index + index * 7
        aoffset = self.getLong3(ioffset + 4)
        address = self.getAddr(aoffset)
        return address


if __name__ == "__main__":
    ip_locater = IpLocater("qqwry.dat")
    ip_locater.output(100, 120)
    ip = '59.64.234.174'
    ip = '58.38.139.229'
    ip = '1.2.127.255'
    ip = '122.9.57.18'
    ip = '63.156.36.95'

    c, a = ip_locater.getIpAddr(ip)
    print "the ip %s come from %s %s" % (ip, a, c)
