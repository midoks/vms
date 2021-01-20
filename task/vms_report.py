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
    if (run_model == '1') or (run_is_master == '1'):
        return True
    return False

#------------Private Methods--------------


def reportData(data):
    _list = common.M('node').field('id,port,name,ip').where(
        'ismaster=?', (1,)).select()

    if len(_list) > 0:
        _url = "http://" + str(_list[0]['ip']) + \
            ":" + str(_list[0]['port'])

        api_url = _url + "/async_master_api/reportData"
        ret = common.httpPost(api_url, {
            "mark": common.getSysKV('run_mark'),
            "data": data,
            'name': _list[0]['name']
        })

        rr = json.loads(ret)
        return rr


def pingServer():
    _list = common.M('node').field('id,port,name,ip').select()

    for x in xrange(0, len(_list)):
        _url = "http://" + str(_list[x]['ip']) + \
            ":" + str(_list[x]['port'])

        api_url = _url + "/async_master_api/ping"
        try:
            ret = common.httpPost(api_url, {
                "mark": common.getSysKV('run_mark'),
                'name': _list[x]['name']
            })
            rr = json.loads(ret)
            if rr['code'] == 0:
                common.M('node').where(
                    'name=?', (_list[x]['name'],)).setField('status', 1)
        except Exception as e:
            common.M('node').where(
                'name=?', (_list[x]['name'],)).setField('status', 0)

    return True


def serverReport():
    time_sleep = 3
    while True:
        if isMasterNode():
            time.sleep(time_sleep)
            continue

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

        time.sleep(time_sleep)


def serverPing():
    while True:
        pingServer()
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

    t = threading.Thread(target=serverPing)
    t.setDaemon(True)
    t.start()

    startTask()
