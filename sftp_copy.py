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
    # Get files: res[[datetime, file name]]
    res = res.split('\n')
    res = filter(lambda item: item.startswith('-'), res)
    res = [item.split()[-2:] for item in res]
    res = map(lambda item: [datetime.strptime(item[0], dt_format), item[1]], res)
    #
    files = []
    # Search last file.
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
        if os.path.exists(item):
            pprint('Exist: {}'.format(item))
            continue
        #
        sp_ds = subprocess.Popen(cmd_cp.format(
            p=ssh_port, k=ssh_pkey,
            u=ssh_user, h=ssh_host,
            d=dir_local, f=item),
            stderr=subprocess.PIPE,
            shell=True
        )
        sp_ds.wait()
        res = sp_ds.communicate()[1]
        #
        # Print error message.
        if res: pprint(res)
        else: pprint('Copy: {}'.format(item))
#
#
def files_clear():
    if copy_count <= 0: return
    #
    for prefix in copy_prefixes:
        files = glob('{}*'.format(prefix))
        #
        while len(files) > copy_count:
            item = min(files, key=lambda item: os.path.getctime(item))
            os.unlink(item)
            pprint('Remove: {}'.format(item))
            files = glob('{}*'.format(prefix))
#
#
if __name__ == '__main__':
    try:
        os.chdir(dir_local)
        files_backup(files_list())
        files_clear()
        #
    except Exception as msg:
        pprint('{}: {}'.format(msg.__class__.__name__, msg))
