# coding: utf-8

#------------------------------
# [从]服务器上报
#------------------------------
import sys
import os
import json
import time
import threading
import subprocess
import shutil

sys.path.append("/usr/local/lib/python2.7/site-packages")
import psutil

root_dir = os.getcwd()
sys.path.append(root_dir + "/class/core")

reload(sys)
sys.setdefaultencoding('utf-8')
import db
import common


#------------Private Methods--------------

def updateStatus(sid, status):
    common.M('video_tmp').where(
        "id=?", (sid,)).setField('status', status)


def isMasterNode():
    run_model = common.getSysKV('run_model')
    run_is_master = common.getSysKV('run_is_master')
    if run_model == '2' and run_is_master == '1':
        return True
    return False

#------------Private Methods--------------


def reloadNingx():
    _list = common.M('kv', 'video').field(
        'name,value').field('name,value').select()
    kv = {}

    for i in xrange(0, len(_list)):
        kv[_list[i]['name']] = _list[i]['value']

    if kv['nginx_domain'] == '':
        return False

    if not os.path.exists(kv['nginx_www']):
        return False

    if not os.path.exists(kv['nginx_video_www']):
        return False

    if kv['nginx_listen'] == '1' and os.path.exists(kv['nginx_path']):
        content = common.readFile('data/nginx_vms.tpl')
        content_to = common.readFile(kv['nginx_path'])

        domain_list = kv['nginx_domain'].split()
        ng_donmain = ' '.join(domain_list)
        content = content.replace('{$NG_DOMAIN}', ng_donmain)

        content = content.replace('{$NG_WWW}', kv['nginx_www'])
        content = content.replace('{$NG_VIDEO_WWW}', kv['nginx_video_www'])

        if kv['nginx_domain_acl'] != '':
            nginx_domain_acl = kv['nginx_domain_acl'].split()
            ng_donmain_acl = ','.join(nginx_domain_acl)
            content = content.replace('{$NG_DOAMIN_ACL}', ng_donmain_acl)
        else:
            content = content.replace('{$NG_DOAMIN_ACL}', '*')

        nginx_bin = [
            '/Applications/mdserver/bin/openresty/bin/nginx'
            '/www/server/nginx/bin/nginx'
        ]

        if common.md5(content) != common.md5(content_to):
            common.writeFile(kv['nginx_path'], content)

            for x in nginx_bin:
                if os.path.exists(x):
                    cmd = x + ' -s reload'
                    print common.execShell(cmd)

    return True


def serverNingx():
    while True:
        reloadNingx()
        time.sleep(10)


def startTask():
    import time
    try:
        while True:
            time.sleep(2)
    except:
        time.sleep(60)
    startTask()

if __name__ == "__main__":

    t = threading.Thread(target=serverNingx)
    t.setDaemon(True)
    t.start()

    startTask()
