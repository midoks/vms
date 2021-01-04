# coding: utf-8

import psutil
import time
import os
import sys
import re
import json
import pwd
import hashlib
from hashlib import md5

from flask import session
from flask import request

from werkzeug.utils import secure_filename
from flask import send_from_directory

sys.path.append(os.getcwd() + "/class/core")
import common


def del_file(path_data):
    for i in os.listdir(path_data):
        file_data = path_data + "/" + i
        if os.path.isfile(file_data) == True:
            os.remove(file_data)
        else:
            del_file(file_data)


def calMD5ForBigFile(file):
    m = md5()
    f = open(file, 'rb')
    buffer = 8192 * 2    # why is 8192 | 8192 is fast than 2048

    while 1:
        chunk = f.read(buffer)
        if not chunk:
            break
        m.update(chunk)

    f.close()
    return m.hexdigest()


def calMD5ForFile(file):
    statinfo = os.stat(file)

    if int(statinfo.st_size) / (1024 * 1024) >= 1000:
        print "File size > 1000, move to big file..."
        return calMD5ForBigFile(file)

    m = md5()
    f = open(file, 'rb')
    m.update(f.read())
    f.close()

    return m.hexdigest()


class video_api:

    def __init__(self):
        pass

    def uploadmd5Api(self):
        if request.method == 'POST':
            upload_file = request.files['file']
            task = request.form.get('task_id')          # 获取文件唯一标识符
            chunk = request.form.get('chunk', 0)        # 获取该分片在所有分片中的序号
            filename = '%s%s' % (task, chunk)           # 构成该分片唯一标识符
            upload_file.save(os.getcwd() + '/tmp/%s' % filename)

        return 'ok'

    def uploadokApi(self):
        target_filename = request.args.get('filename')  # 获取上传文件的文件名
        task = request.args.get('task_id')              # 获取文件的唯一标识符
        chunk = 0                                       # 分片序号
        with open(os.getcwd() + '/tmp/%s' % target_filename, 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = os.getcwd() + '/tmp/%s%d' % (task, chunk)
                    # 按序打开每个分片
                    source_file = open(filename, 'rb')
                    # 读取分片内容写入新文件
                    target_file.write(source_file.read())
                    source_file.close()
                except IOError:
                    break
                chunk += 1
                os.remove(filename)                     # 删除该分片，节约空间
        # 入库
        dirfile = os.path.join(os.getcwd() + '/tmp', target_filename)
        file_md5 = calMD5ForFile(dirfile)
        vmM = common.M('video_tmp')
        r = vmM.add("md5,filename,size,status,uptime,addtime",
                    (file_md5, target_filename, os.path.getsize(dirfile), 0, common.getDate(), common.getDate()))
        print(r)
        if not r:
            return 'fail'
        return 'ok'

    def uploadtestApi(self):
        # 入库
        target_filename = '阴风阵阵.Suspiria.2018.中英字幕.WEBrip.720P-人人影视.mp4'
        dirfile = os.path.join(os.getcwd() + '/tmp', target_filename)
        file_md5 = calMD5ForFile(dirfile)

        return 'ok'
    ##### ----- start ----- ###

    def uploadApi(self):
        file = request.files['file']
        filename = file.filename

        if not os.path.exists(os.getcwd() + '/tmp'):
            os.mkdirs(os.getcwd() + '/tmp')

        dirfile = os.path.join(os.getcwd() + '/tmp', filename)
        file.save(dirfile)

        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '上传成功'

        with open(dirfile, 'rb') as fp:
            data = fp.read()
        file_md5 = hashlib.md5(data).hexdigest()
        vmM = common.M('video_tmp')
        r = vmM.add("md5,filename,size,status,uptime,addtime",
                    (file_md5, filename, os.path.getsize(dirfile), 0, common.getDate(), common.getDate()))

        if not r:
            _ret['code'] = 1
            _ret['msg'] = '入库失败'
        elif not os.path.exists(dirfile):
            _ret['code'] = 1
            _ret['msg'] = '上传失败'

        return common.getJson(_ret)

    def indexApi(self):
        _ret = {}

        limit = request.form.get('limit', '10').encode('utf-8')
        p = request.form.get('p', '1').encode('utf-8')

        start = (int(p) - 1) * (int(limit))

        videoM = common.M('video')
        _list = videoM.field('id,name,filename,size,status,uptime,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        count = videoM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)

    def editApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        name = request.form.get('name', '').encode('utf-8')
        videoM = common.M('video')
        videoM.where('id=?', (sid)).setField('name', name)
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '修改成功'

        return common.getJson(_ret)

    def getApi(self):
        sid = request.args.get('id', '1').encode('utf-8')
        videoM = common.M('video')
        _list = videoM.field('id,name,filename,size,status,uptime,addtime').where(
            'id=?', (sid)).select()
        _ret = {}
        _ret['data'] = _list
        _ret['code'] = 0

        return common.getJson(_ret)

    def delApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        videoM = common.M('video')

        data = videoM.field('id,filename,size').where(
            'id=?', (sid,)).select()
        if data:
            try:
                pathfile = os.getcwd() + "/app/" + str(data[0]['filename'])
                if os.path.exists(pathfile):
                    del_file(pathfile)
                    os.removedirs(pathfile)
            except Exception as e:
                raise e

        r = videoM.where("id=?", (sid,)).delete()
        # print(sid, r)
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '删除成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '删除失败'

        return common.getJson(_ret)

    def tmpApi(self):
        _ret = {}

        limit = request.form.get('limit', '10').encode('utf-8')
        p = request.form.get('p', '1').encode('utf-8')

        start = (int(p) - 1) * (int(limit))

        videoM = common.M('video_tmp')
        _list = videoM.field('id,md5,filename,size,status,uptime,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        count = videoM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)

    def tmpdelApi(self):

        sid = request.form.get('id', '').encode('utf-8')
        videoM = common.M('video_tmp')

        data = videoM.field('id,md5,filename,size').where(
            'id=?', (sid,)).select()

        if data:
            pathfile = os.getcwd() + '/tmp/' + data[0]['filename']
            if os.path.exists(pathfile):
                os.remove(pathfile)

        r = videoM.where("id=?", (sid,)).delete()
        # print(sid, r)
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '删除成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '删除失败'

        return common.getJson(_ret)
