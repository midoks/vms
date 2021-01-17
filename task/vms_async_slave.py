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
    if run_model == '2' and run_is_master == '1':
        return True
    return False


def getNodeList(ismaster=1):
    _list = common.M('node').field('id,info,port,name,ip').where(
        'ismaster=?', (ismaster,)).select()
    return _list


def getTaskList(ismaster=0, status=0):
    _list = common.M('task').field('id,ismaster,mark,sign,vid,status,uptime,addtime').where(
        'ismaster=? and status=?', (ismaster, status,)).limit('1').select()
    return _list


def getMasterNodeURL():
    _list = getNodeList()
    _url = "http://" + str(_list[0]['ip']) + \
        ":" + str(_list[0]['port'])
    return _url
#------------Public Methods--------------


def asyncNodeInfo():
    while True:
        if not isMasterNode():
            print("async Node info !!!")
            _list = common.M('node').field('id,port,name,ip').where(
                'ismaster=?', (1,)).select()
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
        time.sleep(20)


def asyncVideoDBData():
    while True:
        if not isMasterNode():

            # 异步通知已经执行
            video_db_ischange = common.getSysKV('video_db_ischange')
            if video_db_ischange == '1':
                continue
            else:
                common.setSysKV('video_db_ischange', '0')

            print('async VideoDB!!!')
            _list = common.M('node').field('id,port,name,ip').where(
                'ismaster=?', (1,)).select()
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

        time.sleep(20)


def videoDownload(url, pos):
    #print(pos, url)
    fdir = os.path.dirname(pos)
    if not os.path.exists(fdir):
        os.mkdir(fdir)

    c = common.httpGet(url)
    common.writeFile(pos, c)


def asyncVideoFile():
    while True:
        if not isMasterNode():
            task_list = getTaskList(0, 0)
            if len(task_list) > 0:
                print('async VideoFile!!!')
                url = getMasterNodeURL()

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
                        file_url = url + '/' + i.replace('app', 'm3u8')
                        videoDownload(file_url, i)

                common.M('task').where(
                    'id=?', (task_list[0]['id'],)).setField('status', 1)
        time.sleep(10)


def asyncVideoFileCallback():
    while True:
        if not isMasterNode():

            task_list = getTaskList(0, 1)

            if len(task_list) > 0:
                print('async VideoFile Callback!!!')

            for x in xrange(0, len(task_list)):
                url = getMasterNodeURL()
                api_url = url + "/async_master_api/fileAsyncCallBack"

                ret = common.httpPost(api_url, {
                    'mark': common.getSysKV('run_mark'),
                    'name': task_list[x]['mark'],
                    'vid': task_list[x]['vid'],
                })
                data = json.loads(ret)
                if data['code'] != 0:
                    print(data['msg'])
                else:
                    common.M('task').where(
                        'id=?', (task_list[x]['id'],)).setField('status', 2)
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

    # 同步文件完成回调
    t = threading.Thread(target=asyncVideoFileCallback)
    t.setDaemon(True)
    t.start()

    startTask()
