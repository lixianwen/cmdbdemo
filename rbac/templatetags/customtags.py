#!/usr/bin/env python
#coding: utf8

import datetime
from django import template
from django.conf import settings
from asset.models import Asset
from django.urls import reverse
from django.http import QueryDict
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.inclusion_tag('rbac/sidebar.html', takes_context=True)
def sidebar(context):
    request = context['request']
    menu_list = request.session[settings.MENU_SESSION_KEY]
    for menu in menu_list:
        for node in menu['nodes']:
            if request.related_id is not None and node['id'] == request.related_id:
                menu['class'] = 'open'
    return {'menu_list': menu_list}

@register.inclusion_tag('rbac/breadcrumb.html', takes_context=True)
def breadcrumb(context):
    return {'breadcrumb_list': context['request'].breadcrumb_list}

@register.simple_tag(takes_context=True)
def url_handler(context, url_name, *args, **kwargs):
    request = context['request']
    base_url = reverse(url_name, args=args, kwargs=kwargs)
    if not request.GET:
        return base_url
    query = QueryDict(mutable=True)
    query['source'] = request.GET.urlencode()
    return '{0}?{1}'.format(base_url, query.urlencode())
