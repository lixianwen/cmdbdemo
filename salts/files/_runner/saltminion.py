#!/usr/bin/env python

import os
import paramiko
from io import StringIO
from ConfigParser import ConfigParser

c = ConfigParser(allow_no_value=True)
c.read('/path/to/cmdbdemo/cmdb.conf')

def install_6(ip):
    port = int(c.get('ssh', 'port'))
    username = c.get('ssh', 'username')
    password=c.get('ssh', 'password')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, port=port, username=username, password=password)
    s = paramiko.Transport((ip, port))
    s.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(s)
    sftp.put('/srv/salt/_file/install_salt_6.sh', '/usr/local/sbin/install_salt.sh')
    sftp.put('/srv/salt/_file/init_salt_6.sh', '/usr/local/sbin/init_salt.sh')
    try:
        stdin, stdout, stderr = client.exec_command('/bin/sh /usr/local/sbin/install_salt.sh -P')
        writein = StringIO(unicode(stdout.read()))
    except Exception as e:
        raise e
    finally:
        sftp.close()
        s.close()
        client.close()
        writein.close()

def install_7(ip):
    port = int(c.get('ssh', 'port'))
    username = c.get('ssh', 'username')
    password=c.get('ssh', 'password')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, port=port, username=username, password=password)
    s = paramiko.Transport((ip, port))
    s.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(s)
    sftp.put('/srv/salt/_file/install_salt_7.sh', '/usr/local/sbin/install_salt.sh')
    try:
        stdin, stdout, stderr = client.exec_command('/bin/sh /usr/local/sbin/install_salt.sh' + ' ' + ip)
    except Exception as e:
        raise e
    finally:
        sftp.close()
        s.close()
        client.close()
