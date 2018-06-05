# -*- coding: utf-8 -*-
import xlwt
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