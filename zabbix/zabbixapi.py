#!/usr/bin/env python

import os
import sys
import json
import random
import requests
from ConfigParser import ConfigParser

class ZabbixAPI(object):
    def __init__(self):
        self.c = ConfigParser(allow_no_value=True)
        self.c.read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cmdb.conf'))
        self.url = self.c.get('zabbix', 'url')

    def request(self, data):
        try:
             response = requests.post(url=self.url, headers={'Content-Type': 'application/json-rpc'}, data=json.dumps(data))
             return json.loads(response.text)
        except requests.exceptions.ConnectionError as e:
            raise e

    def getToken(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.c.get('zabbix', 'user'),
                "password": self.c.get('zabbix', 'password')
            },
            "id": 1,
            "auth": None
        }
        text = self.request(data)
        return text['result']

    def getHostGroupID(self):
        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": ["groupid", "name"]
#                "filter": {
#                    "name": [
#                        self.hostgroup
#                    ]
#                }
            },
            "auth": self.getToken(),
            "id": 2
        }
        text = self.request(data)
        return text['result']

    def getTemplateID(self):
        data = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": ["templateid", "name"]
#                "filter": {
#                    "host": [
#                        self.template
#                    ]
#                }
            },
            "auth": self.getToken(),
            "id": 3
        }
        text = self.request(data)
        return text['result']

    def hostExists(self, hostname):
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "hostid",
                "filter": {
                    "host": hostname
                }
            },
            "auth": self.getToken(),
            "id": 4
        }
        text = self.request(data)
        if text['result']:
            return True
        else:
            return False

    def getProxyID(self):
        data = {
            "jsonrpc": "2.0",
            "method": "proxy.get",
            "params": {
                "output": "proxyid",
            },
            "auth": self.getToken(),
            "id": 5
        }
        text = self.request(data)
        return random.choice(text['result'])['proxyid']

    def addHost(self, hostname, ip, groupid, templateid):
        data = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostname,
#                "proxy_hostid": self.getProxyID(),                //if use proxy
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": groupid
                    }
                ],
#                "templates": [
#                    {
#                        "templateid": templateid
#                    }
#                ],
                "templates": [{"templateid": i} for i in templateid],
            },
            "auth": self.getToken(),
            "id": 6
        }
        text = self.request(data)
        return text
#        if self.hostExists():
#            print('host {0} is already exists'.format(self.hostname))
#            sys.exit(1)
#        else:
#            text = self.request(data)
#            return text

    def addSnmpDevice(self, hostname, ip, groupid, templateid):
        data = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostname,
#                "proxy_hostid": self.getProxyID(),                //if use proxy
                "interfaces": [
                    {
                        "type": 2,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "161"
                    }
                ],
                "groups": [
                    {
                        "groupid": groupid
                    }
                ],
#                "templates": [
#                    {
#                        "templateid": templateid
#                    }
#                ],
                "templates": [{"templateid": i} for i in templateid],
            },
            "auth": self.getToken(),
            "id": 7
        }
        text = self.request(data)
        return text

    def getHostID(self):
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "host"]
#                "filter": {
#                    "host": self.hostname
#                }
            },
            "auth": self.getToken(),
            "id": 8
        }
        text = self.request(data)
        return text['result']

    def delHost(self, hostid):
        data = {
            "jsonrpc": "2.0",
            "method": "host.delete",
            "params": [hostid],
            "auth": self.getToken(),
            "id": 9
        }
        text = self.request(data)
        return text
#        if self.hostExists():
#            text = self.request(data)
#            return text
#        else:
#            print('host {0} is not exists, can not delete it'.format(self.hostname))
#            sys.exit(1)
