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


def isNeedAsync():
    _list = common.M('node').where(
        'ismaster=?', (1,)).select()
    run_model = common.M('kv').field('id,name,value').where(
        'name=?', ('run_model',)).select()
    # print(run_model[0]['value'], len(_list))
    if run_model[0]['value'] == '2' and len(_list) >= 1:
        return True
    return False


def isMasterNode():
    run_model = common.getSysKV('run_model')
    run_is_master = common.getSysKV('run_is_master')
    if run_model == '2' and run_is_master == '1':
        return True
    return False


def getNodeList(ismaster=1):
    _list = common.M('node').field('id,info,port,name,ip').where(
        'ismaster=?', (ismaster,)).select()
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
    node_list = getNodeList(0)
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


def getTask(vid):
    r = common.M('task').where(
        'vid=?', (vid,)).limit('1').select()
    return r


def addTask(vid, sign, mark):
    return common.M('task').add("ismaster,sign,vid,mark,status,uptime,addtime",
                                (1, sign, vid, mark, 0, common.getDate(), common.getDate()))


def postFileStart(url, vid, name):
    ret = common.httpPost(url, {
        'vid': vid,
        'mark': common.getSysKV('run_mark'),
        'name': name
    })
    if ret:
        return json.loads(ret)
    return False


def postVideoDbAsyncTrigger(url, name):
    ret = common.httpPost(url, {
        'name': name
    })
    if ret:
        return json.loads(ret)
    return False

#------------Public Methods--------------


def funcAsyncVideoFile():
    vlist = common.M('video', 'video').field('id,name').where(
        'node_num=?', (1,)).limit('1').select()
    if len(vlist) > 0:
        print('asyncVideoFile evnet start!!!')

        vid = vlist[0]['id']
        name = vlist[0]['name']
        taskData = getTask(vid)

        pos, data = getMostIdleServer()

        url = getNodeURL(pos)
        apiURL = url + '/async_slave_api/fileStart'
        print(apiURL)
        if len(taskData) == 0:
            r = postFileStart(apiURL, vid, data['name'])
            if r['code'] == 0:
                sign = 'to:' + url
                r = addTask(vid, sign, data['name'])
                if r:
                    print(apiURL + ':' + name + ' 发送成功...')
            else:
                print(common.getSysKV('run_mark') + ':' + r['msg'])
        else:
            print(apiURL + ':' + name + ' 同步中...')

        print('asyncVideoFile evnet end!!!')


def videoDbIsChange():
    '''
    # 由主服务器选择文件同步到那从服务器上
    '''
    mtime = os.stat('data/video.db').st_mtime
    while True:
        if isMasterNode():
            tmp = os.stat('data/video.db').st_mtime
            if tmp != mtime:
                node_list = getNodeList(0)
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
