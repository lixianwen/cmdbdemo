# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

asset_env = (
    (1, U'生产环境'),
    (2, U'测试环境')
    )

asset_status = (
    (1, u"已使用"),
    (2, u"未使用"),
    (3, u'待回收')
    )

ASSET_TYPE = (
    (1, u'虚拟机'),
    (2, u'交换机'),
    (3, u'路由器'),
    (4, u'其他'),
    )

class PhysicalServer(models.Model):
    manufacturer = models.CharField(max_length=32, verbose_name=u'厂商')
    model = models.CharField(max_length=64, verbose_name=u'型号')
    sn = models.CharField(max_length=64, verbose_name=u'序列号')
    ip = models.GenericIPAddressField(protocol='IPv4', verbose_name=u'IP')
    cpu = models.CharField(max_length=64, verbose_name=u'CPU')
    memory = models.CharField(max_length=32, verbose_name=u'内存')
    disk = models.CharField(max_length=32, verbose_name=u'硬盘')
    nic_num = models.PositiveIntegerField(verbose_name=u'网卡数量')
    comment = models.CharField(max_length=128, blank=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.ip
    
    class Meta:
        verbose_name = u"物理服务器"
        verbose_name_plural = verbose_name
        permissions = (
            ("view_ps", "Can see available physical server"),
        )

class IDC(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'机房名称')
    address = models.CharField(max_length=128, blank=True, verbose_name=u"机房地址")
    linkman = models.CharField(max_length=16, blank=True, verbose_name=u'联系人')
    ci = models.CharField(max_length=32, blank=True, verbose_name=u'联系方式')
    bandwidth = models.CharField(max_length=32, blank=True, verbose_name=u'机房带宽')
    ip_segment = models.TextField(blank=True, verbose_name=u"IP地址段")
    comment = models.CharField(max_length=128, blank=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"IDC机房"
        verbose_name_plural = verbose_name
        ordering = ['-id']
        permissions = (
            ("view_idc", "Can see available idc info"),
        )

class Asset(models.Model):
    ip = models.CharField(max_length=16, blank=True, verbose_name=u'电信IP')
    other_ip = models.CharField(max_length=16, blank=True, verbose_name=u'联通IP')
    idc = models.ForeignKey(IDC, verbose_name=u'机房')
    hostname = models.CharField(max_length=32, blank=True)
    cpu = models.CharField(max_length=32, blank=True, verbose_name=u'CPU（核数）')
    memory = models.CharField(max_length=32, blank=True, verbose_name=u'内存（GB）')
    disk = models.CharField(max_length=32, blank=True, verbose_name=u'硬盘（GB）')
    system = models.CharField(max_length=64, blank=True, verbose_name=u"系统")
    status = models.IntegerField(choices=asset_status, blank=True, default=1, verbose_name=u"机器状态")
    asset_type = models.IntegerField(choices=ASSET_TYPE, blank=True, verbose_name=u"主机类型")
    env = models.IntegerField(choices=asset_env, blank=True, verbose_name=u"运行环境")
    host = models.ForeignKey(PhysicalServer, verbose_name=u'宿主机')
    comment = models.CharField(max_length=128, blank=True, verbose_name=u"备注")
    
    def __unicode__(self):
        if self.ip:
            return self.ip
        elif self.other_ip:
            return self.other_ip
        else:
            return self.hostname

    class Meta:
        permissions = (
            ("view_asset", "Can see available asset"),
            ("search_asset", "Can search asset"),
            ("view_hostname", "Can retrieve asset hostname"),
        )
