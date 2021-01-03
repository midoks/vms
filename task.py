# coding: utf-8

#------------------------------
# 计划任务
#------------------------------
import sys
import os
import json
import time
import threading
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

#------------Private Methods--------------

print(has_suffix)


def is_video(path):
    t = os.path.splitext(path)
    if t[1] in self.has_suffix:
        return True
    return False
#------------Private Methods--------------


def printHL():
    print('hello world')


def videoToMp4():
    while True:
        videoM = common.M('video_tmp')

        data = videoM.field('id,filename').where('status=?', (0,)).select()

        for x in data:
            pathfile = os.getcwd() + '/tmp/' + x['filename']
            print(pathfile)

        time.sleep(2)


def videoToM3u8():
    print 'hello world'


def startTask():
    import time
    # 任务队列
    try:
        time.sleep(2)
    except:
        time.sleep(5)
    startTask()

# --------------------------------------PHP监控 end--------------------------------------------- #

if __name__ == "__main__":

    t = threading.Thread(target=printHL)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=videoToMp4)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=videoToM3u8)
    t.setDaemon(True)
    t.start()

    startTask()
