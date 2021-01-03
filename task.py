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

tmp_cmd = os.getcwd() + "/lib/ffmpeg/ffmpeg"
if os.path.exists(tmp_cmd):
    ffmpeg_cmd = tmp_cmd
else:
    ffmpeg_cmd = "/usr/local/bin/ffmpeg"


#------------Private Methods--------------

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
    cmd = ffmpeg_cmd + ' -y -i ' + ts_file + ' -c copy -map 0 -f segment -segment_list ' + \
        m3u8_file + ' -segment_time 10 ' + to_file
    return cmd
#------------Private Methods--------------


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
                common.M('video_tmp').where(
                    "id=?", (x['id'],)).setField('status', 1)
            else:
                pass
        time.sleep(2)


def videoToM3u8():
    while True:
        videoM = common.M('video_tmp')

        data = videoM.field('id,filename').where('status=?', (1,)).select()

        for x in data:
            pathfile = os.getcwd() + '/tmp/' + x['filename']
            print(pathfile)

        time.sleep(2)


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
