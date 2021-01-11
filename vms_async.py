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
#------------Public Methods--------------


def printHL():
    while True:
        print("hello world,vms async!!!")
        time.sleep(3)


def asyncNodeInfo():
    while True:
        print("async node info !!!")
        if isNeedAsync():
            _list = common.M('node').field('id,port,name,ip').where(
                'ismaster=?', (1,)).select()
            _url = "http://" + str(_list[0]['ip']) + \
                ":" + str(_list[0]['port'])

            api_url = _url + "/async_api/node"
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
                    dataList = nodeM.field('id,name,ip,port,ismaster').where(
                        'id=?', (i['id'],)).select()
                    # print dataList
                    # print i
                    if len(dataList) < 1:
                        r = nodeM.add("id,name,ip,port,ismaster,uptime,addtime",
                                      (i['id'], i['name'], i['ip'], i['port'], i['ismaster'], common.getDate(), common.getDate()))
                        if r > 0:
                            print("node add ok")
        time.sleep(20)


def asyncVideoData():

    while True:
        print('async VideoDB!!!')
        if isNeedAsync():
            _list = common.M('node').field('id,port,name,ip').where(
                'ismaster=?', (1,)).select()
            _url = "http://" + str(_list[0]['ip']) + \
                ":" + str(_list[0]['port'])

            api_url = _url + "/async_api/videoInfo"
            pageInfo = common.httpPost(api_url)
            pageInfo = json.loads(pageInfo)

            pageSize = 1024
            pageNum = int(pageInfo['data']) / pageSize
            # print(pageNum, pageInfo['data'])

            api_range_url = _url + "/async_api/videoRange"

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
    t = threading.Thread(target=asyncVideoData)
    t.setDaemon(True)
    t.start()

    startTask()
