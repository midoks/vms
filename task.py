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
# print sys.path

sys.path.append("/usr/local/lib/python2.7/site-packages")
import psutil

sys.path.append(os.getcwd() + "/class/core")
reload(sys)
sys.setdefaultencoding('utf-8')
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


def fg_m3u8_cmd(ts_file, m3u8_file, to_file):
    cmd = ffmpeg_cmd + ' -y -i ' + to_file + ' -c copy -map 0 -f segment -segment_list ' + \
        m3u8_file + ' -segment_time 10 ' + ts_file
    return cmd


def fg_ts_cmd(ts_file, m3u8_file, to_file):
    cmd = ffmpeg_cmd + ' -y -i ' + ts_file + ' -c copy -map 0 -f segment -segment_list ' + \
        m3u8_file + ' -segment_time 10 ' + to_file
    return cmd
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


def printHL():
    print('hello world')


def videoToMp4():
    while True:
        videoM = common.M('video_tmp')
        data = videoM.field('id,filename').where('status=?', (0,)).select()

        for x in data:
            pathfile = os.getcwd() + '/tmp/' + x['filename']
            # print(pathfile)
            if is_mp4(pathfile):
                updateStatus(x['id'], 1)
            else:
                pass
        time.sleep(2)


def videoToTs():
    while True:
        videoM = common.M('video_tmp')
        data = videoM.field('id,md5,filename').where('status=?', (1,)).select()

        tmp_dir = os.getcwd() + '/tmp/'
        for x in data:
            m3u8_file = tmp_dir + x['md5'] + '/' + 'index.m3u8'
            tofile = tmp_dir + x['md5'] + '/' + '%010d.ts'
            pathfile = tmp_dir + x['filename']

            if not os.path.exists(tmp_dir + x['md5']):
                os.mkdir(tmp_dir + x['md5'])

            cmd = fg_m3u8_cmd(tofile, m3u8_file, pathfile)
            print(cmd)
            print execShell(cmd)

        time.sleep(2)


def videoToM3u8():
    while True:
        videoM = common.M('video_tmp')
        data = videoM.field('id,md5,filename').where('status=?', (1,)).select()

        tmp_dir = os.getcwd() + '/tmp/'
        print('videoToM3u8-----@@@start@@@-----')
        for x in data:
            m3u8_file = tmp_dir + x['md5'] + '/' + 'index.m3u8'
            tofile = tmp_dir + x['md5'] + '/' + '%010d.ts'
            pathfile = tmp_dir + x['filename']

            if not os.path.exists(tmp_dir + x['md5']):
                os.mkdir(tmp_dir + x['md5'])

            if not os.path.exists(m3u8_file):
                cmd = fg_m3u8_cmd(tofile, m3u8_file, pathfile)
                data = execShell(cmd)
                print(data[1])
                updateStatus(x['id'], 2)
        print('videoToM3u8-----@@@end@@@-----')
        time.sleep(2)


def videoToDB():
    while True:
        print('videoToDB-----@@@start@@@-----')
        print('videoToDB-----@@@end@@@-----')
        time.sleep(5)


def startTask():
    import time
    # 任务队列
    try:
        time.sleep(2)
    except:
        time.sleep(60)
    startTask()

# --------------------------------------PHP监控 end--------------------------------------------- #

if __name__ == "__main__":

    t = threading.Thread(target=printHL)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=videoToMp4)
    t.setDaemon(True)
    t.start()

    # t = threading.Thread(target=videoToTs)
    # t.setDaemon(True)
    # t.start()

    t = threading.Thread(target=videoToM3u8)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=videoToDB)
    t.setDaemon(True)
    t.start()

    startTask()
