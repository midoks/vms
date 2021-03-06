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
# print sys.path

sys.path.append("/usr/local/lib/python2.7/site-packages")
import psutil

root_dir = os.getcwd()
sys.path.append(root_dir + "/class/core")

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

tmp_cmd = '/www/server/lib/ffmpeg/ffmpeg'
if os.path.exists(tmp_cmd):
    ffmpeg_cmd = tmp_cmd


#------------Private Methods--------------

def updateStatus(sid, status):
    common.M('video_tmp').where(
        "id=?", (sid,)).setField('status', status)


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


def is_video_format(path, format='avi'):
    t = os.path.splitext(path)
    tlen = len(t) - 1
    if t[tlen] == '.' + format:
        return True
    return False


def isDEmpty(data):
    if len(data) > 0:
        return False
    return True


def fg_mp4_cmd(source_file, to_mp4_file):
    cmd = ffmpeg_cmd + ' -y -i "' + source_file + \
        '" -c copy -map 0 "' + to_mp4_file + '"'
    return cmd


def fg_mkv_mp4_cmd(source_file, to_mp4_file):
    cmd = ffmpeg_cmd + ' -y -i "' + source_file + \
        '" -acodec libfaac -vcodec libx264 "' + to_mp4_file + '"'
    return cmd


def fg_m3u8_cmd(ts_file, m3u8_file, to_file):
    cmd = ffmpeg_cmd + ' -y -i "' + to_file + '" -c copy -map 0 -f segment -segment_list ' + \
        m3u8_file + ' -segment_time 3 ' + ts_file
    return cmd


def fg_mdp_cmd(to_file):
    cmd = ffmpeg_cmd + ' -i "' + to_file + \
        '" -media_seg_name vms-\$RepresentationID\$-\$Number%05d\$.m4s -min_seg_duration 1000 -c copy -f dash index.mpd'
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


def videoToMp4():
    while True:
        videoM = common.M('video_tmp')
        data = videoM.field('id,filename').where('status=?', (0,)).select()

        if not isDEmpty(data):
            print('videoToMp4-----@@@start@@@-----')
        for x in data:
            pathfile = root_dir + "/tmp/" + str(x['filename'])
            mp4_file = pathfile + ".mp4"
            # print(pathfile)
            if is_mp4(pathfile):
                updateStatus(x["id"], 1)
            elif is_video_format(pathfile, 'mkv'):
                cmd = fg_mkv_mp4_cmd(pathfile, mp4_file)
                print(cmd)
                os.system(cmd)
                updateStatus(x["id"], 1)
            else:
                cmd = fg_mp4_cmd(pathfile, mp4_file)
                print(cmd)
                os.system(cmd)
                updateStatus(x["id"], 1)

        if not isDEmpty(data):
            print('videoToMp4-----@@@start@@@-----')
        time.sleep(2)


def videoToM3u8():
    while True:
        videoM = common.M('video_tmp')
        data = videoM.field('id,md5,filename').where(
            'status=?', (1,)).limit('1').select()

        tmp_dir = root_dir + '/tmp/'
        app_dir = root_dir + '/app/'

        if not isDEmpty(data):
            print('videoToM3u8-----@@@start@@@-----')
        for x in data:

            tmp_dir_app = tmp_dir + str(x["md5"])

            if not os.path.exists(tmp_dir_app):
                os.mkdir(tmp_dir_app)

            mpd_dir = tmp_dir_app + "/mpd"
            mpd_file = mpd_dir + "/index.mpd"

            m3u8_dir = tmp_dir_app + "/m3u8"
            m3u8_file = m3u8_dir + "/index.m3u8"
            tofile = m3u8_dir + "/%010d.ts"

            pathfile = tmp_dir + str(x["filename"])

            pathfile__tmp = tmp_dir + str(x["filename"]) + ".mp4"
            if os.path.exists(pathfile__tmp):
                pathfile = pathfile__tmp

            if not os.path.exists(pathfile):
                updateStatus(x['id'], 3)
                continue

            if os.path.exists(m3u8_dir):
                os.remove(pathfile)
                print('videoToM3u8----- The file already exists delete ok -----')
                updateStatus(x['id'], 3)
                continue

            # m3u8
            if not os.path.exists(m3u8_dir):
                os.mkdir(m3u8_dir)

            if not os.path.exists(m3u8_file):
                cmd = fg_m3u8_cmd(tofile, m3u8_file, pathfile)
                print(cmd)
                os.system(cmd)
                updateStatus(x['id'], 2)

            # # mpd
            # if not os.path.exists(mpd_dir):
            #     os.mkdir(mpd_dir)

            # # print(mpd_file)
            # if not os.path.exists(mpd_file):
            #     mpd_cmd = fg_mdp_cmd(pathfile)

            #     mpd_cmd = "cd " + mpd_dir + " && " + mpd_cmd
            #     print(mpd_cmd)
            #     os.system(mpd_cmd)

        if not isDEmpty(data):
            print('videoToM3u8-----@@@end@@@-----')
        time.sleep(3)


def videoToDB():
    while True:
        videoM = common.M('video_tmp')
        run_mark = common.getSysKV('run_mark')
        viM = common.M('video', 'video')
        vinodeM = common.M('video_node', 'video')
        data = videoM.field('id,md5,filename,size,filename').where(
            'status=?', (2,)).select()
        tmp_dir = root_dir + "/tmp/"
        app_dir = root_dir + "/app/"
        if not isDEmpty(data):
            print('videoToDB-----@@@start@@@-----')
        for x in data:
            m3u8_dir = tmp_dir + str(x["md5"])
            source_file = tmp_dir + str(x['filename'])
            source_file_tmp = tmp_dir + str(x['filename']) + ".mp4"
            if os.path.exists(m3u8_dir):
                data = viM.field('id').where(
                    "filename=?", (x["md5"],)).select()

                if not data:
                    pid = viM.add("name,filename,size,status,node_num,uptime,addtime",
                                  (x['filename'], x['md5'], x['size'], 0, 1, common.getDate(), common.getDate()))
                    vinodeM.add("pid,node_id,addtime", (pid,
                                                        run_mark, common.getDate()))
                    shutil.move(m3u8_dir, app_dir)
                    os.remove(source_file)
                    if os.path.exists(source_file_tmp):
                        os.remove(source_file_tmp)

                updateStatus(x['id'], 3)
        if not isDEmpty(data):
            print('videoToDB-----@@@end@@@-----')
        time.sleep(2)


def videoToDel():
    while True:

        videoM = common.M('video_tmp')
        data = videoM.field('id,md5,filename,size,filename').where(
            'status=?', (3,)).select()

        if not isDEmpty(data):
            print('videoToDel-----@@@start@@@-----')
        tmp_dir = root_dir + "/tmp/"
        app_dir = root_dir + "/app/"
        for x in data:
            m3u8_dir = tmp_dir + str(x["md5"])
            source_file = tmp_dir + str(x['filename'])

            r = videoM.where("id=?", (x['id'],)).delete()
            if r:
                print(x['filename'] + ' delete ok!!!')
            else:
                print(x['filename'] + 'delete fail!!!')

        if not isDEmpty(data):
            print('videoToDel-----@@@end@@@-----')
        time.sleep(5)


def startTask():
    import time
    try:
        while True:
            time.sleep(2)
    except:
        time.sleep(60)
    startTask()

if __name__ == "__main__":

    t = threading.Thread(target=videoToMp4)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=videoToM3u8)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=videoToDB)
    t.setDaemon(True)
    t.start()

    t = threading.Thread(target=videoToDel)
    t.setDaemon(True)
    t.start()

    startTask()
