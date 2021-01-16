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

_has_suffix = ['mp4', 'rmvb', 'flv', 'avi',
               'mpg', 'mkv', 'wmv', 'avi', 'rm']
has_suffix = []
for x in range(len(_has_suffix)):
    has_suffix.append('.' + _has_suffix[x])
    has_suffix.append('.' + _has_suffix[x].upper())

tmp_cmd = os.getcwd() + "/lib/ffmpeg/ffmpeg"
if os.path.exists(tmp_cmd):
    ffmpeg_cmd = tmp_cmd
else:
    ffmpeg_cmd = "/usr/local/bin/ffmpeg"

tmp_cmd = '/www/server/lib/ffmpeg/ffmpeg'
if os.path.exists(tmp_cmd):
    ffmpeg_cmd = tmp_cmd


#------------Private Methods--------------

def updateStatus(sid, status):
    common.M('video_tmp').where(
        "id=?", (sid,)).setField('status', status)

# print(has_suffix, ffmpeg_cmd)


def is_video(path):
    t = os.path.splitext(path)
    if t[1] in has_suffix:
        return True
    return False


def is_mp4(path):
    t = os.path.splitext(path)
    tlen = len(t) - 1
    if t[tlen] == '.mp4':
        return True
    return False


def isDEmpty(data):
    if len(data) > 0:
        return False
    return True
#------------Private Methods--------------

#------------Public Methods--------------


def execShell(cmdstring, cwd=None, timeout=None, shell=True):

    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,
                           shell=shell, bufsize=4096, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout：%s" % cmdstring)

    return sub.communicate()


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

#------------Public Methods--------------


def asyncVideoFile():
    '''
    # 由主服务器选择文件同步到那从服务器上
    '''
    while True:
        if isMasterNode():
            vlist = common.M('video', 'video').field('id,name').where(
                'node_num=?', (1,)).limit('1').select()

            if len(vlist) > 0:
                vid = vlist[0]['id']
                name = vlist[0]['name']
                taskData = getTask(vid)

                pos, data = getMostIdleServer()

                url = getNodeURL(pos)
                apiURL = url + '/async_slave_api/fileStart'
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
        time.sleep(3)


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
