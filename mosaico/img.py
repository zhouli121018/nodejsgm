# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
from PIL import Image, ImageDraw

#判断文件是否为有效（完整）的图片
#输入参数为bytes，如网络请求返回的二进制数据
def IsValidImage4Bytes(buf):
    bValid = True
    try:
        Image.open(io.BytesIO(buf)).verify()
    except:
        bValid = False

    return bValid


#判断文件是否为有效（完整）的图片
#输入参数为bytes，如网络请求返回的二进制数据
def IsValidImage4Bytes(buf):
    bValid = True
    if buf[6:10] in (b'JFIF', b'Exif'):     #jpg图片
        if not buf.rstrip(b'\0\r\n').endswith(b'\xff\xd9'):
            bValid = False
    else:
        try:
            Image.open(io.BytesIO(buf)).verify()
        except:
            bValid = False

    return bValid

def get_placeholder_image(width, height):
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle([(0, 0), (width, height)], fill=(0x70, 0x70, 0x70))
    # stripes
    x = 0
    y = 0
    size = 40
    while y < height:
        draw.polygon([(x, y), (x + size, y), (x + size*2, y + size), (x + size*2, y + size*2)], fill=(0x80, 0x80, 0x80))
        draw.polygon([(x, y + size), (x + size, y + size*2), (x, y + size*2)], fill=(0x80, 0x80, 0x80))
        x = x + size*2
        if (x > width):
            x = 0
            y = y + size*2
    return image



