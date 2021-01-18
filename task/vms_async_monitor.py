# coding: utf-8

#------------------------------
# video 数据同步监控
#------------------------------
import sys
import os
import json
import time
import threading
import subprocess
import shutil
import base64


sys.path.append("/usr/local/lib/python2.7/site-packages")
import psutil

sys.path.append(os.getcwd() + "/class/core")

reload(sys)
sys.setdefaultencoding('utf-8')


import requests
import db
import common


#------------Private Methods--------------

def updateStatus(sid, status):
    common.M('video_tmp').where(
        "id=?", (sid,)).setField('status', status)


def isDEmpty(data):
    if len(data) > 0:
        return False
    return True
#------------Private Methods--------------

#------------Public Methods--------------


def isMasterNode():
    run_model = common.getSysKV('run_model')
    run_is_master = common.getSysKV('run_is_master')
    if run_model == '2' and run_is_master == '1':
        return True
    return False


def getNodeList(ismaster=1, status=0):
    _list = common.M('node').field('id,info,port,name,ip').where(
        'ismaster=? and status=?', (ismaster, status,)).select()
    return _list


def postVideoDbAsyncTrigger(url, name):
    ret = common.httpPost(url, {
        'name': name
    })
    if ret:
        return json.loads(ret)
    return False

#------------Public Methods--------------


def videoDbIsChange():
    '''
    # Video DB 发送改变!由主服务器选择文件同步到那从服务器上
    '''
    mtime = os.stat('data/video.db').st_mtime
    while True:
        if isMasterNode():
            tmp = os.stat('data/video.db').st_mtime
            if tmp != mtime:
                node_list = getNodeList(0, 1)
                for x in xrange(0, len(node_list)):
                    # print(node_list[x])
                    url = 'http://' + node_list[x]['ip'] + \
                        ':' + node_list[x]['port'] + \
                        '/async_slave_api/videoDbAsyncTrigger'
                    try:
                        r = postVideoDbAsyncTrigger(url, node_list[x]['name'])
                        if r and r['code'] == 0:
                            print("DB文件发生改变通知成功:" + url)
                        else:
                            print("DB文件发生改变通知失败:" + url)
                    except Exception as e:
                        print("DB文件发生改变通知失败:" + url + ':', e)

            mtime = tmp
        time.sleep(2)


def startTask():
    import time
    try:
        while True:
            time.sleep(2)
    except:
        time.sleep(60)
    startTask()

if __name__ == "__main__":

    # 同步文件
    t = threading.Thread(target=videoDbIsChange)
    t.setDaemon(True)
    t.start()

    startTask()
