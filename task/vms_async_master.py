# coding: utf-8

#------------------------------
# 计划任务
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


def getMasterNodeURL():
    _list = getNodeList()
    _url = "http://" + str(_list[0]['ip']) + \
        ":" + str(_list[0]['port'])
    return _url


def getMostIdleServer():
    '''
    获取最空闲服务器
    '''
    node_list = getNodeList(0, 1)
    mi = 1000000
    pos = 0

    if len(node_list) > 0:
        for i in range(0, len(node_list)):
            if node_list[i]['info']:
                info = json.loads(node_list[i]['info'])

                runLoad = info['one'] / info['max'] * 100
                if runLoad < mi:
                    mi = runLoad
                    pos = i

        ii = node_list[pos]
        return ii['id'], ii
    return '', False


def getNodeByID(nid):
    _list = common.M('node').field(
        'id,ip,port,name').where('id=?', (nid,)).select()
    return _list[0]


def getNodeURL(nid):
    d = getNodeByID(nid)
    url = "http://" + str(d['ip']) + ":" + str(d['port'])
    return url


def getTask(vid, status=0):
    r = common.M('task').where(
        'vid=? and status=?', (vid, status)).limit('1').select()
    return r


def getTaskList(ismaster=0, status=0):
    _list = common.M('task').field('id,ismaster,mark,sign,vid,status,uptime,addtime').where(
        'ismaster=? and status=?', (ismaster, status,)).limit('1').select()
    return _list


def addTask(vid, action, sign, mark):
    return common.M('task').add("ismaster,action,sign,vid,mark,status,uptime,addtime",
                                (1, action, sign, vid, mark, 0, common.getDate(), common.getDate()))


def postFileStart(url, vid, action, name):
    ret = common.httpPost(url, {
        'vid': vid,
        'action': action,
        'mark': common.getSysKV('run_mark'),
        'name': name
    })
    if ret:
        return json.loads(ret)
    return False

#------------Public Methods--------------


def funcAsyncVideoFile():
    vlist = common.M('video', 'video').field('id,name').where(
        'node_num=?', (1,)).limit('1').select()
    if len(vlist) < 1:
        return

    print('asyncVideoFile evnet start!!!')

    vid = vlist[0]['id']
    name = vlist[0]['name']
    taskData = getTask(vid)

    pos, data = getMostIdleServer()
    if not data:
        print('node server ping fail!!')
        return

    url = getNodeURL(pos)
    apiURL = url + '/async_slave_api/fileStart'
    # print(apiURL)
    if len(taskData) == 0:
        r = postFileStart(apiURL, vid, 1, data['name'])
        if r['code'] == 0:
            sign = 'to:' + url
            r = addTask(vid, 1, sign, data['name'])
            if r:
                print(apiURL + ':' + name + ' 发送成功...')
        else:
            print(common.getSysKV('run_mark') + ':' + r['msg'])
    else:
        print(apiURL + ':' + name + ' 同步中...')

    print('asyncVideoFile evnet end!!!')
    return


def asyncVideoFile():
    '''
    # 由主服务器选择文件同步到那从服务器上
    '''
    time_sleep = 3
    while True:
        if not isMasterNode():
            time.sleep(time_sleep)
            continue
        try:
            funcAsyncVideoFile()
        except Exception as e:
            print(e)
        time.sleep(time_sleep)


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
    t = threading.Thread(target=asyncVideoFile)
    t.setDaemon(True)
    t.start()

    startTask()
