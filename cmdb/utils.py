#!/usr/bin/env python
#coding:utf8

import re
from rest_framework.views import exception_handler

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
