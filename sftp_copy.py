#!/usr/bin/env python2
#-*- coding: utf-8 -*-
import os
import subprocess
from glob import glob
from pprint import pprint
from datetime import datetime
#
#
ssh_host = 'server'
ssh_user = 'backup'
ssh_port = '22'
ssh_pkey = '/var/backup/.ssh/srv_key'
#
dir_server = '/var/backup'
dir_local  = '/var/backup'
copy_prefixes = ['backup']
copy_count = 3
#
#
dt_format  = '%d-%m-%Y'
dt_current = datetime.now()
#
def files_list():
    cmd_ls = 'ssh \'{u}@{h}\' -p {p} -i \'{k}\' \'{c}\''
    #
    sp_ds = subprocess.Popen(cmd_ls.format(
        u=ssh_user, h=ssh_host,
        p=ssh_port, k=ssh_pkey,
        c='ls -l --time-style \'+{f}\' {d}/'.format(f=dt_format, d=dir_server)),
        stdout=subprocess.PIPE,
        shell=True
    )
    sp_ds.wait()
    res = sp_ds.communicate()[0]
    #
    res = res.split('\n')
    res = filter(lambda item: item.startswith('-'), res)
    res = [item.split()[-2:] for item in res]
    res = map(lambda item: [datetime.strptime(item[0], dt_format), item[1]], res)
    #
    files = []
    for item in copy_prefixes:
        tmp = filter(lambda key: key[1].startswith(item), res)
        tmp = max(tmp, key=lambda item: item[0])
        files.append(tmp[1])
    #
    return files
#
#
def files_backup(files):
    cmd_cp = 'scp -P {p} -i \'{k}\' -q \'{u}@{h}:{d}/{f}\' \'.\''
    #
    for item in files:
        sp_ds = subprocess.Popen(cmd_cp.format(
            p=ssh_port, k=ssh_pkey,
            u=ssh_user, h=ssh_host,
            d=dir_local, f=item),
            stderr=subprocess.PIPE,
            shell=True
        )
        sp_ds.wait()
        res = sp_ds.communicate()[1]
        if res: pprint(res)
#
#
def files_clear():
    if os.getcwd() != dir_local: os.chdir(dir_local)
    #
    files = os.listdir('.')

    return files
#
#
try:
    os.chdir(dir_local)
    #files_backup(files_list())
    #files_clear()
    #
except Exception as msg:
    pprint('{}: {}'.format(msg.__class__.__name__, msg))
