#!/bin/bash

ip=$1

if [ $# -ne 1 ]
then
    echo "缺少参数：IP"
    exit 1
fi

sed -i 's/#master: salt/master: 192.168.0.125/' /etc/salt/minion
sed -i "s/#id:/id: $ip/" /etc/salt/minion

/etc/init.d/salt-minion restart
