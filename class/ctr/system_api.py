# coding: utf-8

import psutil
import time
import os
import re
import math
import json
import sys

from flask import Flask, session
from flask import request

import db
import common
import requests
import config_api


from threading import Thread
from time import sleep

reload(sys)
sys.setdefaultencoding('utf-8')


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


class system_api:
    setupPath = None
    pids = None

    def __init__(self):
        self.setupPath = common.getServerDir()

    ##### ----- start ----- ###

    def updateKV(self, name, value):
        return common.M('kv').where('name=?', (name,)).setField('value', value)

    def editApi(self):
        run_model = request.form.get('run_model', '').encode('utf-8')
        video_size = request.form.get('video_size', '').encode('utf-8')

        self.updateKV('run_model', run_model)
        self.updateKV('video_size', video_size)

        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '修改成功'

        return common.getJson(_ret)

    def getApi(self):
        sid = request.args.get('id', '').encode('utf-8')
        kvM = common.M('kv')
        _list = kvM.field('id,name,value').select()
        _ret = {}
        _ret['data'] = _list
        _ret['code'] = 0
        return common.getJson(_ret)

    def systemTotalApi(self):
        data = self.getSystemTotal()
        return mw.getJson(data)

    def setControlApi(self):
        stype = request.form.get('type', '')
        day = request.form.get('day', '')
        data = self.setControl(stype, day)
        return data

    def getLoadAverageApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getLoadAverageData(start, end)
        return mw.getJson(data)

    def getCpuIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getCpuIoData(start, end)
        return mw.getJson(data)

    def getDiskIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getDiskIoData(start, end)
        return mw.getJson(data)

    def getNetworkIoApi(self):
        start = request.args.get('start', '')
        end = request.args.get('end', '')
        data = self.getNetWorkIoData(start, end)
        return mw.getJson(data)

    # 重启面板
    def restartApi(self):
        self.restartMw()
        return mw.returnJson(True, '已重启!')
    ##### ----- end ----- ###

    @async
    def restartMw(self):
        sleep(0.3)
        cmd = mw.getRunDir() + '/scripts/init.d/vms restart'
        common.execShell(cmd)

    @async
    def restartServer(self):
        if not mw.isRestart():
            return mw.returnJson(False, '请等待所有安装任务完成再执行!')
        mw.execShell("sync && init 6 &")
        return mw.returnJson(True, '命令发送成功!')

        # 名取PID
    def getPid(self, pname):
        try:
            if not self.pids:
                self.pids = psutil.pids()
            for pid in self.pids:
                if psutil.Process(pid).name() == pname:
                    return True
            return False
        except:
            return False

    # 检查端口是否占用
    def isOpen(self, port):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('127.0.0.1', int(port)))
            s.shutdown(2)
            return True
        except:
            return False

    # 检测指定进程是否存活
    def checkProcess(self, pid):
        try:
            if not self.pids:
                self.pids = psutil.pids()
            if int(pid) in self.pids:
                return True
            return False
        except:
            return False

    def getSystemTotal(self, interval=1):
        # 取系统统计信息
        data = self.getMemInfo()
        cpu = self.getCpuInfo(interval)
        data['cpuNum'] = cpu[1]
        data['cpuRealUsed'] = cpu[0]
        data['time'] = self.getBootTime()
        data['system'] = self.getSystemVersion()
        return data

    def getLoadAverage(self):
        c = os.getloadavg()
        data = {}
        data['one'] = float(c[0])
        data['five'] = float(c[1])
        data['fifteen'] = float(c[2])
        data['max'] = psutil.cpu_count() * 2
        data['limit'] = data['max']
        data['safe'] = data['max'] * 0.75
        return data

    def getSystemVersion(self):
        # 取操作系统版本
        if mw.getOs() == 'darwin':
            data = mw.execShell('sw_vers')[0]
            data_list = data.strip().split("\n")
            mac_version = ''
            for x in data_list:
                mac_version += x.split("\t")[1] + ' '
            return mac_version

        version = mw.readFile('/etc/redhat-release')
        if not version:
            version = mw.readFile(
                '/etc/issue').strip().split("\n")[0].replace('\\n', '').replace('\l', '').strip()
        else:
            version = version.replace('release ', '').strip()
        return version

    def getBootTime(self):
        # 取系统启动时间
        start_time = psutil.boot_time()
        run_time = time.time() - start_time
        # conf = mw.readFile('/proc/uptime').split()
        tStr = float(run_time)
        min = tStr / 60
        hours = min / 60
        days = math.floor(hours / 24)
        hours = math.floor(hours - (days * 24))
        min = math.floor(min - (days * 60 * 24) - (hours * 60))
        return mw.getInfo('已不间断运行: {1}天{2}小时{3}分钟', (str(int(days)), str(int(hours)), str(int(min))))

    def getCpuInfo(self, interval=1):
        # 取CPU信息
        cpuCount = psutil.cpu_count()
        used = psutil.cpu_percent(interval=interval)
        return used, cpuCount

    def getMemInfo(self):
        # 取内存信息
        mem = psutil.virtual_memory()
        if mw.getOs() == 'darwin':
            memInfo = {
                'memTotal': mem.total / 1024 / 1024
            }
            memInfo['memRealUsed'] = memInfo['memTotal'] * (mem.percent / 100)
        else:
            memInfo = {
                'memTotal': mem.total / 1024 / 1024,
                'memFree': mem.free / 1024 / 1024,
                'memBuffers': mem.buffers / 1024 / 1024,
                'memCached': mem.cached / 1024 / 1024
            }

            memInfo['memRealUsed'] = memInfo['memTotal'] - \
                memInfo['memFree'] - memInfo['memBuffers'] - \
                memInfo['memCached']
        return memInfo

    def getMemUsed(self):
        # 取内存使用率
        try:
            import psutil
            mem = psutil.virtual_memory()

            if mw.getOs() == 'darwin':
                return mem.percent

            memInfo = {'memTotal': mem.total / 1024 / 1024, 'memFree': mem.free / 1024 / 1024,
                       'memBuffers': mem.buffers / 1024 / 1024, 'memCached': mem.cached / 1024 / 1024}
            tmp = memInfo['memTotal'] - memInfo['memFree'] - \
                memInfo['memBuffers'] - memInfo['memCached']
            tmp1 = memInfo['memTotal'] / 100
            return (tmp / tmp1)
        except Exception, ex:
            return 1

    def getDiskInfo(self, get=None):
        return self.getDiskInfo2()
        # 取磁盘分区信息
        diskIo = psutil.disk_partitions()
        diskInfo = []

        for disk in diskIo:
            if disk[1] == '/mnt/cdrom':
                continue
            if disk[1] == '/boot':
                continue
            tmp = {}
            tmp['path'] = disk[1]
            tmp['size'] = psutil.disk_usage(disk[1])
            diskInfo.append(tmp)
        return diskInfo

    def getDiskInfo2(self):
        # 取磁盘分区信息
        temp = mw.execShell(
            "df -h -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
        tempInodes = mw.execShell(
            "df -i -P|grep '/'|grep -v tmpfs | grep -v devfs")[0]
        temp1 = temp.split('\n')
        tempInodes1 = tempInodes.split('\n')
        diskInfo = []
        n = 0
        cuts = ['/mnt/cdrom', '/boot', '/boot/efi', '/dev',
                '/dev/shm', '/run/lock', '/run', '/run/shm', '/run/user']
        for tmp in temp1:
            n += 1
            inodes = tempInodes1[n - 1].split()
            disk = tmp.split()
            if len(disk) < 5:
                continue
            if disk[1].find('M') != -1:
                continue
            if disk[1].find('K') != -1:
                continue
            if len(disk[5].split('/')) > 4:
                continue
            if disk[5] in cuts:
                continue
            arr = {}
            arr['path'] = disk[5]
            tmp1 = [disk[1], disk[2], disk[3], disk[4]]
            arr['size'] = tmp1
            arr['inodes'] = [inodes[1], inodes[2], inodes[3], inodes[4]]
            if disk[5] == '/':
                bootLog = os.getcwd() + '/tmp/panelBoot.pl'
                if disk[2].find('M') != -1:
                    if os.path.exists(bootLog):
                        os.system('rm -f ' + bootLog)
                else:
                    if not os.path.exists(bootLog):
                        pass
            if inodes[2] != '0':
                diskInfo.append(arr)
        return diskInfo

    # 清理系统垃圾
    def clearSystem(self, get):
        count = total = 0
        tmp_total, tmp_count = self.ClearMail()
        count += tmp_count
        total += tmp_total
        tmp_total, tmp_count = self.ClearOther()
        count += tmp_count
        total += tmp_total
        return count, total

    def getNetWork(self):
        # return self.GetNetWorkApi(get);
        # 取网络流量信息
        try:
            # 取网络流量信息
            networkIo = psutil.net_io_counters()[:4]
            if not "otime" in session:
                session['up'] = networkIo[0]
                session['down'] = networkIo[1]
                session['otime'] = time.time()

            ntime = time.time()
            networkInfo = {}
            networkInfo['upTotal'] = networkIo[0]
            networkInfo['downTotal'] = networkIo[1]
            networkInfo['up'] = round(float(
                networkIo[0] - session['up']) / 1024 / (ntime - session['otime']), 2)
            networkInfo['down'] = round(
                float(networkIo[1] - session['down']) / 1024 / (ntime - session['otime']), 2)
            networkInfo['downPackets'] = networkIo[3]
            networkInfo['upPackets'] = networkIo[2]

            # print networkIo[1], session['down'], ntime, session['otime']
            session['up'] = networkIo[0]
            session['down'] = networkIo[1]
            session['otime'] = time.time()

            networkInfo['cpu'] = self.getCpuInfo()
            networkInfo['load'] = self.getLoadAverage()
            networkInfo['mem'] = self.getMemInfo()

            return networkInfo
        except Exception, e:
            print e
            return None

    def getNetWorkApi(self):
        # 取网络流量信息
        try:
            tmpfile = 'data/network.temp'
            networkIo = psutil.net_io_counters()[:4]

            if not os.path.exists(tmpfile):
                mw.writeFile(tmpfile, str(
                    networkIo[0]) + '|' + str(networkIo[1]) + '|' + str(int(time.time())))

            lastValue = mw.readFile(tmpfile).split('|')

            ntime = time.time()
            networkInfo = {}
            networkInfo['upTotal'] = networkIo[0]
            networkInfo['downTotal'] = networkIo[1]
            networkInfo['up'] = round(
                float(networkIo[0] - int(lastValue[0])) / 1024 / (ntime - int(lastValue[2])), 2)
            networkInfo['down'] = round(
                float(networkIo[1] - int(lastValue[1])) / 1024 / (ntime - int(lastValue[2])), 2)
            networkInfo['downPackets'] = networkIo[3]
            networkInfo['upPackets'] = networkIo[2]

            mw.writeFile(tmpfile, str(
                networkIo[0]) + '|' + str(networkIo[1]) + '|' + str(int(time.time())))

            # networkInfo['cpu'] = self.GetCpuInfo(0.1)
            return networkInfo
        except:
            return None

    def getNetWorkIoData(self, start, end):
        # 取指定时间段的网络Io
        data = mw.M('network').dbfile('system').where("addtime>=? AND addtime<=?", (start, end)).field(
            'id,up,down,total_up,total_down,down_packets,up_packets,addtime').order('id asc').select()
        return self.toAddtime(data)

    def getDiskIoData(self, start, end):
        # 取指定时间段的磁盘Io
        data = mw.M('diskio').dbfile('system').where("addtime>=? AND addtime<=?", (start, end)).field(
            'id,read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime').order('id asc').select()
        return self.toAddtime(data)

    def getCpuIoData(self, start, end):
        # 取指定时间段的CpuIo
        data = mw.M('cpuio').dbfile('system').where("addtime>=? AND addtime<=?",
                                                    (start, end)).field('id,pro,mem,addtime').order('id asc').select()
        return self.toAddtime(data, True)

    def getLoadAverageData(self, start, end):
        data = mw.M('load_average').dbfile('system').where("addtime>=? AND addtime<=?", (
            start, end)).field('id,pro,one,five,fifteen,addtime').order('id asc').select()
        return self.toAddtime(data)

    # 格式化addtime列
    def toAddtime(self, data, tomem=False):
        import time
        if tomem:
            import psutil
            mPre = (psutil.virtual_memory().total / 1024 / 1024) / 100
        length = len(data)
        he = 1
        if length > 100:
            he = 1
        if length > 1000:
            he = 3
        if length > 10000:
            he = 15
        if he == 1:
            for i in range(length):
                data[i]['addtime'] = time.strftime(
                    '%m/%d %H:%M', time.localtime(float(data[i]['addtime'])))
                if tomem and data[i]['mem'] > 100:
                    data[i]['mem'] = data[i]['mem'] / mPre

            return data
        else:
            count = 0
            tmp = []
            for value in data:
                if count < he:
                    count += 1
                    continue
                value['addtime'] = time.strftime(
                    '%m/%d %H:%M', time.localtime(float(value['addtime'])))
                if tomem and value['mem'] > 100:
                    value['mem'] = value['mem'] / mPre
                tmp.append(value)
                count = 0
            return tmp
