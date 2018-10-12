#!/usr/bin/env python

import time
import salt.config
import salt.client

def get(minion, function, params):
    __opts__ = salt.config.client_config('/etc/salt/master')
    conf_file = __opts__['conf_file']
    localclient = salt.client.LocalClient(conf_file)
    jid = localclient.cmd_async(minion, function, [i.strip() for i in params.split(',')])
    return jid
    wait_time = 0
    sleep_interval = 1
    while wait_time < __opts__['timeout']:
        print('wait {0} seconds'.format(wait_time))
        result = localclient.get_cache_returns(jid)
        if result:
            print(type(result))
            return result
        time.sleep(sleep_interval)
        wait_time += sleep_interval

def get_no_param(minion, function):
    __opts__ = salt.config.client_config('/etc/salt/master')
    conf_file = __opts__['conf_file']
    localclient = salt.client.LocalClient(conf_file)
    jid = localclient.cmd_async(minion, function)
    wait_time = 0
    sleep_interval = 1
    while wait_time < __opts__['timeout']:
        print('wait {0} seconds'.format(wait_time))
        result = localclient.get_cache_returns(jid)
        if result:
            print(type(result))
            return result
        time.sleep(sleep_interval)
        wait_time += sleep_interval
