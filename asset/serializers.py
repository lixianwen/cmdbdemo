#!/usr/bin/env python
#coding:utf8

from cmdb.utils import validIPV4
from rest_framework import serializers
from models import Asset, IDC, PhysicalServer

class AssetSerializer(serializers.HyperlinkedModelSerializer):
    idc_name = serializers.CharField(source='idc.name')
    belong_to = serializers.IPAddressField(source='host.ip')
    status = serializers.CharField(source='get_status_display')
    asset_type = serializers.CharField(source='get_asset_type_display')
    env = serializers.CharField(source='get_env_display')
#    status = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ('url', 'ip', 'other_ip', 'idc_name', 'hostname', 'cpu', 'memory', 'disk', 'system', 'status', 'asset_type', 'env', 'belong_to', 'comment')

    def validate_belong_to(self, value):
        if not PhysicalServer.objects.filter(ip=value).exists():
            raise serializers.ValidationError('PhysicalServer matching query does not exist')
        return value

    def validate_idc_name(self, value):
        if not IDC.objects.filter(name=value).exists():
            raise serializers.ValidationError('IDC matching query does not exist')
        return value

    def validate_ip(self, value):
        if value:
            if not validIPV4(value):
                raise serializers.ValidationError(u'IP地址不合法')
        return value

    def validate_other_ip(self, value):
        if value:
            if not validIPV4(value):
                raise serializers.ValidationError(u'IP地址不合法')
        return value

#    def to_representation(self, instance):
#        '''add human-readable suffix for `cpu` `memory` `disk`'''
#        ret = super(AssetSerializer, self).to_representation(instance)
#        if ret['cpu']:
#            ret['cpu'] = ret['cpu'] + u'核'
#        if ret['memory']:
#            ret['memory'] = ret['memory'] + 'GB'
#        if ret['disk']:
#            ret['disk'] = ret['disk'] + 'GB'
#        return ret

#    def get_status(self, obj):
#        return obj.get_status_display()
