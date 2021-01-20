# coding: utf-8

import psutil
import time
import os
import sys
import re
import json
import pwd
import hashlib


reload(sys)
sys.setdefaultencoding('utf-8')

from flask import session
from flask import request

from werkzeug.utils import secure_filename
from flask import send_from_directory

sys.path.append(os.getcwd() + "/class/core")
import common

import base64


from threading import Thread


def updateNodeNum(vid):
    node_num = common.M('video_node', 'video').where(
        "pid=?", (vid,)).count()
    common.M('video', 'video').where(
        'id=?', (vid,)).setField('node_num', node_num)
    return True


class async_master_api:

    def __init__(self):
        pass

    def isNameRight(self):
        name = request.form.get('name', '0').encode('utf-8')
        mark = common.getSysKV('run_mark')
        if name != mark:
            return common.retFail('name is error!')
        return ''

    def pingApi(self):
        return common.retOk('ok')

    def nodeApi(self):
        '''
        由从服务器发送请求,同步节点信息
        '''

        r = self.isNameRight()
        if r != '':
            return r

        source = request.form.get('source').encode('utf-8')
        source = source.replace("'", '"').replace("u", '')

        rr = json.loads(source)
        nodeM = common.M('node')

        retList = nodeM.field('id,name,ip,port,info,ismaster').where(
            'name<>?', (rr['name'],)).select()
        if len(retList) > 100:
            return common.retFail('too many nodes!')

        dataList = nodeM.field('id,name,ip,port,info,ismaster').where(
            'name=?', (rr['name'],)).select()
        if len(dataList) < 1:

            rAdd = nodeM.add("name,ip,port,ismaster,uptime,addtime", (rr['name'], rr[
                'ip'], rr['port'], rr['ismaster'], common.getDate(), common.getDate()))

            if not rAdd:
                return common.retFail()
            return common.retOk('ok', retList)
        else:
            return common.retOk('already exists!', retList)

    def videoDbInfoApi(self):
        '''
        由从服务器发送请求,同步video db 数据
        '''
        dsize = os.path.getsize('data/video.db')
        return common.retOk('ok', dsize)

    def videoDbRangeApi(self):
        '''
        由从服务器发送请求,同步video db 数据
        '''
        start = request.form.get('start', '0').encode('utf-8')
        slen = request.form.get('slen', '1024').encode('utf-8')
        c = common.readFilePos('data/video.db', start, slen)
        return common.retOk('ok', base64.b64encode(c))

    def reportDataApi(self):
        '''
        由从服务器发送请求,同步服务器负载信息
        '''

        r = self.isNameRight()
        if r != '':
            return r

        data = request.form.get('data', '').encode('utf-8')
        data = data.replace("'", '"').replace("u", '')
        mark = request.form.get('mark', '').encode('utf-8')
        up1 = common.M('node').where(
            'name=?', (mark,)).setField('info', data)

        if not up1:
            return common.retFail()
        return common.retOk()

    def fileListApi(self):
        '''
        文件信息列表
        '''
        r = self.isNameRight()
        if r != '':
            return r

        vid = request.form.get('vid', '').encode('utf-8')

        dd = common.M('video', 'video').field(
            'id,name,filename,size,status,node_num,uptime,addtime').where('id=?', (vid,)).select()

        if len(dd) < 1:
            return common.retFail('video not exists!!!')

        fdir = "app/" + dd[0]['filename']

        if not os.path.exists(fdir):
            return common.retFail('dir not exists!!!')

        flist = common.fileList(fdir)

        return common.retOk('ok', flist)

    def fileAsyncCallBackApi(self):
        '''
        文件完成回调
        '''
        # r = self.isNameRight()
        # if r != '':
        #     return r

        vid = request.args.get('vid', '').encode('utf-8')
        mark = request.args.get('mark', '').encode('utf-8')
        # print(vid, mark)
        r = common.M('task').where(
            'vid=? and mark=?', (vid, mark)).setField('status', 1)

        vlist = common.M('video_node', 'video').where(
            "pid=? and node_id=?", (vid, mark,)).select()

        if len(vlist) > 0:
            updateNodeNum(vid)
            return common.retFail('already exists!!!')

        common.M('video_node', 'video').add(
            "pid,node_id,addtime", (vid, mark, common.getDate()))
        updateNodeNum(vid)
        if not r:
            return common.retFail()
        return common.retOk()
