#!/usr/bin/env python

import os
import json
import requests
from ConfigParser import ConfigParser

class SaltAPI(object):
    def __init__(self):
        self.s = requests.session()
        self.c = ConfigParser(allow_no_value=True)
        self.c.read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cmdb.conf'))
        self.url = self.c.get('salt', 'url')

    def getToken(self):
        login_url = '{0}/login'.format(self.url)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        dic = {
            'username': self.c.get('salt', 'user'),
            'password': self.c.get('salt', 'password'), 
            'eauth': self.c.get('salt', 'eauth')
        }
        result = self.s.post(login_url, headers=headers, data=dic, verify=False).text
        return json.loads(result)['return'][0]['token']

    def header(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/x-yaml',
            'X-Auth-Token': self.getToken()
        }
        return headers

    def cmd(self, ip, command):
        dic = {
            'client': 'local',
            'tgt': ip,
            'fun': 'cmd.run',
            'arg': [command]
        }
#        dic = {
#            'client': 'runner',
#            'fun': 'getresult.get',
#            'arg': [ip, 'cmd.run', command]
#        }
        response = self.s.post(self.url, headers=self.header(), data=dic, verify=False).text
        return response

    def minion(self, ip, release):
        dic = {
            'client': 'runner',
            'fun': release,
            'arg': ip,
        }
        response = self.s.post(self.url, headers=self.header(), data=dic, verify=False).text
        return response

    def pushFile(self, ip, source, dest):
        dic = {
            'client': 'runner',
            'fun': 'getresult.get',
            'arg': [ip, 'cp.get_file', "{0}, {1}".format('salt://' + source, dest)]
        }
#        dic = {
#            'client': 'local',
#            'tgt': ip,
#            'fun': 'cp.get_file',
#            'arg': ['salt://' + source, dest]
#        }
        response = self.s.post(self.url, headers=self.header(), data=dic, verify=False).text
        return response

    def getReuslt(self, jid):
        headers = {
            'Accept': 'application/x-yaml',
            'X-Auth-Token': self.getToken()
        }
        url = self.url + '/jobs/' + jid
        response = self.s.get(url, headers=headers, verify=False).text
        return response

    def exeScript(self, ip, filename):
        dic = {
            'client': 'runner',
            'fun': 'getresult.get',
            'arg': [ip, 'cmd.script', '{0}'.format('salt://' + filename)]
        }
        response = self.s.post(self.url, headers=self.header(), data=dic, verify=False).text
        return response
