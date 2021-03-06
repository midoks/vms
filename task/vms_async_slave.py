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


def download(url, file_path):
    # 第一次请求是为了得到文件总大小
    r1 = request.get(url, stream=True, verify=False)
    total_size = int(r1.headers['Content-Length'])

    # 这重要了，先看看本地文件下载了多少
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0
    # 显示一下下载了多少
    print(temp_size)
    print(total_size)
    # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
    headers = {'Range': 'bytes=%d-' % temp_size}
    # 重新请求网址，加入新的请求头的
    r = requests.get(url, stream=True, verify=False, headers=headers)

    # 下面写入文件也要注意，看到"ab"了吗？
    # "ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()

                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % (
                    '█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()  # 避免上面\r 回车符


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
    if (run_model == '1') or (run_is_master == '1'):
        return True
    return False


def getNodeList(ismaster=1):
    _list = common.M('node').field('id,info,port,name,ip').where(
        'ismaster=?', (ismaster,)).select()
    return _list


def getTaskList(ismaster=0, status=0, action=1):
    _list = common.M('task').field('id,ismaster,mark,sign,vid,status,action,uptime,addtime').where(
        'ismaster=? and status=? and action=?', (ismaster, status, action)).limit('1').select()
    return _list


def getMasterNodeURL():
    _list = getNodeList()
    _url = "http://" + str(_list[0]['ip']) + \
        ":" + str(_list[0]['port'])
    return _url


def postNode(_list):
    ret = common.httpPost(api_url, {
        'source': {
            "name": common.getSysKV('run_mark'),
            "ip": common.getLocalIp(),
            "port": common.readFile('data/port.pl'),
            "ismaster": common.getSysKV('run_is_master')
        },
        'name': _list[0]['name']

    })

    retDic = json.loads(ret)
#------------Public Methods--------------


def asyncNodeInfo():
    sleep_time = 20
    while True:
        if isMasterNode():
            time.sleep(sleep_time)
            continue

        _list = common.M('node').field('id,port,name,ip').where(
            'ismaster=?', (1,)).select()

        if len(_list) < 1:
            time.sleep(sleep_time)
            continue

        print("async Node info !!! start")
        _url = "http://" + str(_list[0]['ip']) + \
            ":" + str(_list[0]['port'])

        api_url = _url + "/async_master_api/node"
        ret = common.httpPost(api_url, {
            'source': {
                "name": common.getSysKV('run_mark'),
                "ip": common.getLocalIp(),
                "port": common.readFile('data/port.pl'),
                "ismaster": common.getSysKV('run_is_master')
            },
            'name': _list[0]['name']

        })
        retDic = json.loads(ret)

        if retDic['code'] == 0:
            nodeM = common.M('node')
            for i in retDic['data']:
                dataList = nodeM.field('name,ip,port,ismaster').where(
                    'name=?', (i['name'],)).select()
                if len(dataList) < 1:
                    r = nodeM.add("name,ip,port,info,ismaster,uptime,addtime",
                                  (i['name'], i['ip'], i['port'], i['info'], i['ismaster'], common.getDate(), common.getDate()))
                    if r > 0:
                        print("node add ok")
                else:
                    r = nodeM.where('name=?', (i['name'],)).save('ip,port,info,ismaster,uptime', (i[
                        'ip'], i['port'], i['info'], i['ismaster'], common.getDate()))
                    if r > 0:
                        print("node update ok")
        print("async Node info !!! end")
        time.sleep(sleep_time)


def asyncVideoDBData():
    sleep_time = 3
    while True:
        if isMasterNode():
            time.sleep(sleep_time)
            continue

        # 异步通知已经执行
        video_db_ischange = common.getSysKV('video_db_ischange')
        if video_db_ischange == '0':
            time.sleep(sleep_time)
            continue

        _list = common.M('node').field('id,port,name,ip').where(
            'ismaster=?', (1,)).select()

        if len(_list) < 1:
            time.sleep(sleep_time)
            continue

        print('async VideoDB!!!')

        _url = "http://" + str(_list[0]['ip']) + \
            ":" + str(_list[0]['port'])

        api_url = _url + "/async_master_api/videoDbInfo"
        pageInfo = common.httpPost(api_url)
        pageInfo = json.loads(pageInfo)

        pageSize = 1024
        pageNum = int(pageInfo['data']) / pageSize
        # print(pageNum, pageInfo['data'])

        api_range_url = _url + "/async_master_api/videoDbRange"

        common.writeFileClear('data/tmp.db')
        for x in xrange(0, pageNum):
            start = x * pageSize

            data = common.httpPost(api_range_url, {
                'start': start,
                'slen': pageSize,
            })
            data = json.loads(data)
            fdata = base64.b64decode(data['data'])
            common.writeFileAppend('data/tmp.db', fdata)

        tmpMd5 = common.calMD5ForFile('data/tmp.db')
        videoMd5 = common.calMD5ForFile('data/video.db')

        if tmpMd5 != videoMd5:
            os.remove('data/video.db')
            os.rename('data/tmp.db', 'data/video.db')

        print('async VideoDB ok!!!')
        common.setSysKV('video_db_ischange', '0')
        time.sleep(sleep_time)


def videoDownload(url, pos):
    # print(pos, url)
    fdir = os.path.dirname(pos)
    if not os.path.exists(fdir):
        common.mkdir(fdir)
    c = common.httpGet(url)
    common.writeFile(pos, c)


def asyncVideoFile():
    sleep_time = 3
    while True:
        if isMasterNode():
            time.sleep(sleep_time)
            continue
        task_list = getTaskList(0, 0)
        if len(task_list) < 1:
            time.sleep(sleep_time)
            continue

        url = getMasterNodeURL()

        print('async VideoFile!!!')
        api_url = url + "/async_master_api/fileList"
        ret = common.httpPost(api_url, {
            'vid': task_list[0]['vid'],
            'name': task_list[0]['mark']
        })

        if ret:
            r = json.loads(ret)
            if r['code'] != 0:
                print(r['msg'])
                continue

            for i in r['data']:
                file_url = url + '/' + i.replace('app', 'v')
                videoDownload(file_url, i)

        common.M('task').where(
            'id=?', (task_list[0]['id'],)).setField('status', 1)
        time.sleep(sleep_time)


def asyncVideoFileDel():
    sleep_time = 20
    while True:
        if isMasterNode():
            time.sleep(sleep_time)
            continue

        task_list = task_list = getTaskList(0, 0, 2)
        if len(task_list) < 1:
            time.sleep(sleep_time)
            continue

        print('async asyncVideoFileDel!!!')
        sign = task_list[0]['sign']
        filename = sign.split('|')[1]

        pathfile = os.getcwd() + "/app/" + filename
        if os.path.exists(pathfile):
            common.execShell('rm -rf ' + pathfile)
            if os.path.exists(pathfile):
                del_file(pathfile)
                os.removedirs(pathfile)

            common.M('task').where(
                'id=?', (task_list[0]['id'],)).setField('status', 1)

        time.sleep(sleep_time)


def asyncTaskCallBack():
    sleep_time = 3
    while True:
        if isMasterNode():
            time.sleep(sleep_time)
            continue

        task_list = _list = common.M('task').field('id,ismaster,mark,sign,vid,status,action,uptime,addtime').where(
            'ismaster=? and status=?', (0, 1)).limit('1').select()

        if len(task_list) < 1:
            time.sleep(sleep_time)
            continue

        print('async asyncTask Callback!!!')
        for x in xrange(0, len(task_list)):
            url = getMasterNodeURL()
            api_url = url + "/async_master_api/asyncTaskCallBack"
            ret = common.httpPost(api_url, {
                'mark': common.getSysKV('run_mark'),
                'name': task_list[x]['mark'],
                'vid': task_list[x]['vid'],
                'action': task_list[x]['action'],
            })
            data = json.loads(ret)
            if data['code'] != 0:
                print(data['msg'])
            else:
                common.M('task').where(
                    'id=?', (task_list[x]['id'],)).setField('status', 2)
        time.sleep(sleep_time)


def startTask():
    import time
    try:
        while True:
            time.sleep(2)
    except:
        time.sleep(60)
    startTask()

if __name__ == "__main__":

    # 同步节点数据
    t = threading.Thread(target=asyncNodeInfo)
    t.setDaemon(True)
    t.start()

    # 全量同步
    t = threading.Thread(target=asyncVideoDBData)
    t.setDaemon(True)
    t.start()

    # 同步文件
    t = threading.Thread(target=asyncVideoFile)
    t.setDaemon(True)
    t.start()

    # 同步文件删除
    t = threading.Thread(target=asyncVideoFileDel)
    t.setDaemon(True)
    t.start()

    # 同步文件完成回调
    t = threading.Thread(target=asyncTaskCallBack)
    t.setDaemon(True)
    t.start()

    startTask()
