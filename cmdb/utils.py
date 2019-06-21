#!/usr/bin/env python
#coding:utf8

import re
import os
import subprocess
import xlsxwriter
from django.conf import settings
from rest_framework.views import exception_handler
from django.urls import RegexURLPattern, RegexURLResolver

r = re.compile(r'[\.]+')

def validIPV4(ip):      
    split_ip = r.split(ip)
    if len(split_ip) != 4:
        print('IP地址格式不正确')
        return False
    for num in split_ip:
        if num.isdigit():
            if int(num) not in xrange(0, 256):
                print('IP地址不合法')
                return False
        else:
            print('IP地址不合法, 含非数字')
            return False
    return True

def customExceptionHandler(exception, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exception, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
    return response

def export(filename, model):
    export_file = os.path.join(settings.BASE_DIR, 'tpl', filename)
    if os.path.exists(export_file):
        returncode = subprocess.call(['rm', '-rf', export_file])
    workbook = xlsxwriter.Workbook(export_file)
    worksheet = workbook.add_worksheet('sheet1')
    worksheet.set_first_sheet()

    format_title = workbook.add_format()
    format_title.set_border(1)
    format_title.set_align('center')
    format_title.set_bold()

    format_body = workbook.add_format()
    format_body.set_border(1)
    format_body.set_align('center')
    format_body.set_align('vcenter')
    format_body.set_text_wrap()

    queryset = model.objects.values()
    keys = list(queryset)[0].keys()
    key_col = 0
    for key in keys:
        worksheet.write(0, key_col, key, format_title)
        key_col += 1

    row = 1
    col = 0
    i = 1
    
    for item in queryset:
        for k, v in item.iteritems():
            worksheet.write(row, col, v, format_body)
            col += 1
        row += 1
        col = 0
    
    workbook.close()

class AddClass(object):
    def __init__(self, fields):
        for name, field in fields.iteritems():
            if hasattr(field.widget, 'input_type'):
                if field.widget.input_type == 'select':
                    field.widget.attrs['class'] = 'form-control chosen-select'
                else:
                    field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

def excludeWhiteURLs(url):
    for reg in settings.VALID_URL_LIST:
        if re.match(reg, url):
            return True

def getAllURLs(url_list, url_dict, prefix, namespace=None):
    '''
    Get all the apps urls, except which one in white list setting in settings.py
    :param url_list -- the url pattenrs provided by urls model
    :param url_dict -- use for store the result
    :param prefix -- prefix for splice url
    '''
    for entry in url_list:
        if isinstance(entry, RegexURLPattern):
            # Not include urls which did not define url name
            if not entry.name:
                continue

            name = '{0}:{1}'.format(namespace, entry.name) if namespace else entry.name
            url = prefix + entry.regex.pattern
            url = url.replace('^', '').replace('$', '')

            # Exclude some urls in white list
            if excludeWhiteURLs(url):
                continue
            
            url_dict[name] = {
                'url_pattern_name': name,
                'url': url
            }
        elif isinstance(entry, RegexURLResolver):
            getAllURLs(entry.url_patterns, url_dict, prefix+entry.regex.pattern, entry.namespace)
