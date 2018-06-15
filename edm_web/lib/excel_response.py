# -*- coding: utf-8 -*-

import xlwt
import random
import datetime
from django.http import HttpResponse

COLOR_CHOICE = [0x32, 0x34, 0x2E, 0x36]

class ExcelResponse(HttpResponse):

    def __init__(self, data, output_name='excel_data', headers=None, force_csv=False, encoding='utf8'):

        # Make sure we've got the right type of data to work with
        valid_data = False
        if hasattr(data, '__getitem__'):
            if isinstance(data[0], dict):
                if headers is None:
                    headers = data[0].keys()
                data = [[row[col] for col in headers] for row in data]
                data.insert(0, headers)
            if hasattr(data[0], '__getitem__'):
                valid_data = True
        assert valid_data is True, "ExcelResponse requires a sequence of sequences"

        import StringIO
        output = StringIO.StringIO()
        # Excel has a limit on number of rows; if we have more than that, make a csv
        use_xls = False
        if len(data) <= 65536 and force_csv is not True:
            try:
                import xlwt
            except ImportError:
                # xlwt doesn't exist; fall back to csv
                pass
            else:
                use_xls = True
        if use_xls:
            book = xlwt.Workbook(encoding=encoding)
            sheet = book.add_sheet('Sheet 1')
            styles = {'datetime': xlwt.easyxf(num_format_str='yyyy-mm-dd hh:mm:ss'),
                      'date': xlwt.easyxf(num_format_str='yyyy-mm-dd'),
                      'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
                      'default': xlwt.Style.default_style}

            for rowx, row in enumerate(data):
                for colx, value in enumerate(row):
                    if isinstance(value, datetime.datetime):
                        cell_style = styles['datetime']
                    elif isinstance(value, datetime.date):
                        cell_style = styles['date']
                    elif isinstance(value, datetime.time):
                        cell_style = styles['time']
                    else:
                        cell_style = styles['default']
                    sheet.write(rowx, colx, value, style=cell_style)
            book.save(output)
            mimetype = 'application/vnd.ms-excel'
            file_ext = 'xls'
        else:
            for row in data:
                out_row = []
                for value in row:
                    if not isinstance(value, basestring):
                        value = unicode(value)
                    value = value.encode(encoding)
                    out_row.append(value.replace('"', '""'))
                output.write('"%s"\n' % '","'.join(out_row))
            mimetype = 'text/csv'
            file_ext = 'csv'
        output.seek(0)
        if not isinstance(output_name, basestring):
            output_name = unicode(output_name)
        output_name = output_name.encode(encoding)
        super(ExcelResponse, self).__init__(content=output.getvalue(), content_type=mimetype)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % (output_name.replace('"', '\"'), file_ext)

class MultiSheetExcelResponse(HttpResponse):

    def __init__(self, data, max_count, output_name='excel_data', force_csv=False, encoding='utf8'):

        # Excel has a limit on number of rows; if we have more than that, make a csv
        # data: [('sheetname', lists), ...]
        import StringIO
        output = StringIO.StringIO()
        use_xls = False
        if max_count <= 65536 and force_csv is not True:
            try:
                import xlwt
            except ImportError:
                # xlwt doesn't exist; fall back to csv
                pass
            else:
                use_xls = True

        if use_xls:
            book = xlwt.Workbook(encoding=encoding)
            styles = {'datetime': xlwt.easyxf(num_format_str='yyyy-mm-dd hh:mm:ss'),
                      'date': xlwt.easyxf(num_format_str='yyyy-mm-dd'),
                      'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
                      'default': xlwt.Style.default_style}
            for sheetname, count, lists in data:
                sheet = book.add_sheet(sheetname)
                for rowx, row in enumerate(lists):
                    for colx, value in enumerate(row):
                        if isinstance(value, datetime.datetime):
                            cell_style = styles['datetime']
                        elif isinstance(value, datetime.date):
                            cell_style = styles['date']
                        elif isinstance(value, datetime.time):
                            cell_style = styles['time']
                        else:
                            cell_style = styles['default']
                        sheet.write(rowx, colx, value, style=cell_style)
            book.save(output)
            mimetype = 'application/vnd.ms-excel'
            file_ext = 'xls'
        else:
            for sheetname, count, lists in data:
                for row in lists:
                    out_row = []
                    for value in row:
                        if not isinstance(value, basestring):
                            value = unicode(value)
                        value = value.encode(encoding)
                        out_row.append(value.replace('"', '""'))
                    output.write('"%s"\n' % '","'.join(out_row))
            mimetype = 'text/csv'
            file_ext = 'csv'
        output.seek(0)
        if not isinstance(output_name, basestring):
            output_name = unicode(output_name)
        output_name = output_name.encode(encoding)
        super(MultiSheetExcelResponse, self).__init__(content=output.getvalue(), content_type=mimetype)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % (output_name.replace('"', '\"'), file_ext)

class FormatExcelResponse(HttpResponse):

    def __init__(self, data, output_name='excel_data', headers=None, force_csv=False, encoding='utf8', mimetype=None, file_ext=None):

        valid_data = False
        if hasattr(data, '__getitem__'):
            if isinstance(data[0], dict):
                if headers is None:
                    headers = data[0].keys()
                data = [[row[col] for col in headers] for row in data]
                data.insert(0, headers)
            if hasattr(data[0], '__getitem__'):
                valid_data = True
        assert valid_data is True, "ExcelResponse requires a sequence of sequences"

        import StringIO
        output = StringIO.StringIO()
        if file_ext == 'csv':
            for row in data:
                out_row = []
                for value in row:
                    if not isinstance(value, basestring):
                        value = unicode(value)
                    value = value.encode(encoding)
                    out_row.append(value.replace('"', '""'))
                output.write('"%s"\n' % '","'.join(out_row))
        elif file_ext == 'txt':
            for row in data:
                out_row = ''
                for value in row:
                    if not isinstance(value, basestring):
                        value = unicode(value)
                    value = value.encode(encoding)
                    out_row += value + u'；'.encode(encoding)
                output.write('%s\n' % out_row)
        elif file_ext == 'xls':
            book = xlwt.Workbook(encoding=encoding)
            sheet = book.add_sheet('Sheet 1')
            cell_style = xlwt.Style.default_style
            for rowx, row in enumerate(data):
                for colx, value in enumerate(row):
                    value = unicode(value)
                    sheet.write(rowx, colx, value, style=cell_style)
            book.save(output)
        elif file_ext == 'xlsx':
            import xlsxwriter
            # 讲xlsx数据写入数据流中
            xlsxdata = xlsxwriter.Workbook(output)
            # 新增一个格式，范例为日期格式，其他格式可以参考官方文档
            # date_format = xlsxdata.add_format({'num_format': u'yyyy"年"m"月"d"日"'})
            worksheet = xlsxdata.add_worksheet('Sheet 1')
            res = data[0]
            for i in range(len(res)):
                worksheet.write(0, i, res[i])
            xlsxdata.close()

        output.seek(0)
        super(FormatExcelResponse, self).__init__(content=output.getvalue(), content_type=mimetype)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % (output_name.replace('"', '\"'), file_ext)

class DHeadExcelResponse(HttpResponse):

    def __init__(self, data, output_name='excel_data', headers=None, footer=None, encoding='utf8'):

        '''
        -- headers
        [
            [u'日期', (0, 1, 0, 0), []],
            [u'客户名称', (0, 1, 1, 1), []],
            [u'Web发送量统计', (0, 0, 2, 4), [[u'任务量',(1, 2)], [u'失败量',(1, 3)], [u'发送量',(1, 4)]]],
            [u'错误地址', (0, 1, 5, 5), []],
            [u'预统计/扣点', (0, 0, 6, 7), [[u'发送量',(1, 6)], [u'预扣点',(1, 7)]]],
            [u'实际统计/扣点', (0, 0, 8, 11), [[u'实际发送',(1, 8)], [u'投递失败',(1, 9)], [u'拒绝投递',(1, 10)], [u'实际扣点',(1, 11)]]],
        ]
        -- footer
        [u'总计', (12, 12, 0, 1), [[u'任务量',(12, 2)], [u'失败量',(12, 3)], [u'发送量',(12, 4)],...]]
        '''
        import StringIO
        output = StringIO.StringIO()

        book = xlwt.Workbook(encoding=encoding)
        sheet = book.add_sheet('Sheet 1')
        styles = {'datetime': xlwt.easyxf(num_format_str='yyyy-mm-dd hh:mm:ss'),
                  'date': xlwt.easyxf(num_format_str='yyyy-mm-dd'),
                  'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
                  'default': xlwt.Style.default_style}
        headers = headers if isinstance(headers, list) else []
        footer = footer if isinstance(footer, list) else []
        h_xfstyle = set_style(pattern_fore_colour=random.choice(COLOR_CHOICE))
        f_xfstyle = set_style(pattern_fore_colour=0x09, horz=0x03, vert=0x02)
        for each in headers:
            field, pos_field, line_field = each
            sheet.write_merge(pos_field[0], pos_field[1], pos_field[2], pos_field[3], unicode(field), style=h_xfstyle)
            for line in line_field:
                sheet.write(line[1][0], line[1][1], unicode(line[0]), style=h_xfstyle)
        if footer:
            field, pos_field, line_field = footer
            sheet.write_merge(pos_field[0], pos_field[1], pos_field[2], pos_field[3], unicode(field), style=f_xfstyle)
            for line in line_field:
                sheet.write(line[1][0], line[1][1], line[0], style=styles['default'])

        for rowx, row in enumerate(data):
            for colx, value in enumerate(row):
                if isinstance(value, datetime.datetime):
                    cell_style = styles['datetime']
                elif isinstance(value, datetime.date):
                    cell_style = styles['date']
                elif isinstance(value, datetime.time):
                    cell_style = styles['time']
                else:
                    cell_style = styles['default']
                sheet.write(rowx+2, colx, value, style=cell_style)
        book.save(output)
        mimetype = 'application/vnd.ms-excel'
        file_ext = 'xls'

        output.seek(0)
        if not isinstance(output_name, basestring):
            output_name = unicode(output_name)
        output_name = output_name.encode(encoding)
        super(DHeadExcelResponse, self).__init__(content=output.getvalue(), content_type=mimetype)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % (output_name.replace('"', '\"'), file_ext)

def set_style(name='Times New Roman', height=240, bold=True, pattern_fore_colour=0x1E, horz=0x02, vert=0x01):
    style = xlwt.XFStyle() # 初始化样式

    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    # font.italic = True
    font.shadow = True
    font.color_index = 4
    font.height = height
    style.font = font

    borders= xlwt.Borders()# 边框
    borders.left= 1
    borders.right= 1
    borders.top= 1
    borders.bottom= 1
    style.borders = borders

    pattern = xlwt.Pattern() # 背景颜色
    pattern.pattern = pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = pattern_fore_colour
    style.pattern = pattern

    alignment = xlwt.Alignment() # 字体居中
    alignment.horz = horz
    alignment.vert = vert
    style.alignment = alignment

    return style

_colour_map_text = """
aqua 0x31
black 0x08
blue 0x0C
blue_gray 0x36
bright_green 0x0B
brown 0x3C
coral 0x1D
cyan_ega 0x0F
dark_blue 0x12
dark_blue_ega 0x12
dark_green 0x3A
dark_green_ega 0x11
dark_purple 0x1C
dark_red 0x10
dark_red_ega 0x10
dark_teal 0x38
dark_yellow 0x13
gold 0x33
gray_ega 0x17
gray25 0x16
gray40 0x37
gray50 0x17
gray80 0x3F
green 0x11
ice_blue 0x1F
indigo 0x3E
ivory 0x1A
lavender 0x2E
light_blue 0x30
light_green 0x2A
light_orange 0x34
light_turquoise 0x29
light_yellow 0x2B
lime 0x32
magenta_ega 0x0E
ocean_blue 0x1E
olive_ega 0x13
olive_green 0x3B
orange 0x35
pale_blue 0x2C
periwinkle 0x18
pink 0x0E
plum 0x3D
purple_ega 0x14
red 0x0A
rose 0x2D
sea_green 0x39
silver_ega 0x16
sky_blue 0x28
tan 0x2F
teal 0x15
teal_ega 0x15
turquoise 0x0F
violet 0x14
white 0x09
yellow 0x0D
"""
