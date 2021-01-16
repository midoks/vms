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


class async_slave_api:

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

    def videoInfoApi(self):
        '''
        由从服务器发送请求,同步video db 数据
        '''
        dsize = os.path.getsize('data/video.db')
        return common.retOk('ok', dsize)

    def videoRangeApi(self):
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

    def fileStartApi(self):
        '''
        由主服务器发送请求,从服务器同步文件
        '''
        r = self.isNameRight()
        if r != '':
            return r

        mark = request.form.get('mark', '').encode('utf-8')
        vid = request.form.get('vid', '').encode('utf-8')

        vlist = common.M('video', 'video').where('id=?', vid).select()
        if len(vlist) < 1:
            return common.retFail('video doesn\'t exist, maybe syncing data...!!!')

        nlist = common.M('node').field(
            'id,info,port,name,ip').where('name=?', (mark,)).select()
        if len(nlist) < 1:
            return common.retFail('node info doesn\'t exist, maybe syncing data...!!!')

        rlist = common.M('task').where('vid=?', (vid,)).limit('1').select()
        if len(rlist) > 0:
            return common.retFail('the task already exists...!!!')
        # print()
        url = nlist[0]['ip'] + ':' + nlist[0]['port']
        sign = 'from:' + url
        r = common.M('task').add("ismaster,sign,vid,mark,status,uptime,addtime",
                                 (0, sign, vid, mark, 0, common.getDate(), common.getDate()))
        if not r:
            return common.retFail('the task add fail...!!!')
        return common.retOk()
