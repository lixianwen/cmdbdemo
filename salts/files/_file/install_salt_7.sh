#!/bin/bash

ip=$1

yum install -y https://repo.saltstack.com/yum/redhat/salt-repo-latest-2.el7.noarch.rpm
yum clean expire-cache
yum install -y salt-minion
sed -i 's/#master: salt/master: 192.168.0.125/' /etc/salt/minion
sed -i "s/#id:/id: $ip/" /etc/salt/minion
systemctl restart salt-minion
