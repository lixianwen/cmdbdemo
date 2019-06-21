#!/usr/bin/env python
#coding: utf8

import re
import sys
from django import template
from django.conf import settings
from django.urls import resolve, reverse

register = template.Library()

r = re.compile(r'/(\w+)/')

@register.filter
def has_permission(value, name):
    permission_mapping = value.session.get(settings.PERMISSION_SESSION_KEY)
    return True if name in permission_mapping else False

@register.filter
def hightlight(value):
    url_object = resolve(value.path_info)
    current_path = value.path_info
    namespace = url_object.namespace
    prefix = r.match(current_path)
    prefix = prefix.group(1) if prefix else ''
    if sys.version_info.major == 2:
        return True if re.match(namespace, prefix) else False
    elif sys.version_info < (3, 4):
        raise Exception('Need Python version at least 3.4 or higher')
    else:
        return True if re.fullmatch(namespace, prefix) else False
