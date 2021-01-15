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


def isNeedAsync():
    _list = common.M('node').where(
        'ismaster=?', (1,)).select()
    run_model = common.M('kv').field('id,name,value').where(
        'name=?', ('run_model',)).select()
    # print(run_model[0]['value'], len(_list))
    if run_model[0]['value'] == '2' and len(_list) >= 1:
        return True
    return False

#------------Private Methods--------------


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


def reportData(data):
    _list = common.M('node').field('id,port,name,ip').where(
        'ismaster=?', (1,)).select()

    if len(_list) > 0:
        _url = "http://" + str(_list[0]['ip']) + \
            ":" + str(_list[0]['port'])

        api_url = _url + "/async_api/reportData"
        ret = common.httpPost(api_url, {
            "mark": common.getSysKV('run_mark'),
            "data": data,
            'name': _list[0]['name']
        })

        rr = json.loads(ret)
        return rr


def serverReport():
    while True:
        if isNeedAsync():
            c = os.getloadavg()
            data = {}
            data['one'] = float(c[0])
            data['five'] = float(c[1])
            data['fifteen'] = float(c[2])
            data['max'] = psutil.cpu_count() * 2
            data['limit'] = data['max']
            data['safe'] = data['max'] * 0.75
            data['report_time'] = common.getDate()

            r = reportData(data)
            if r['code'] != 0:
                print('同步失败![%s]', common.getDate())

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

    t = threading.Thread(target=serverReport)
    t.setDaemon(True)
    t.start()

    startTask()