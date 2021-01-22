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

    def videoDbAsyncTriggerApi(self):
        r = self.isNameRight()
        if r != '':
            return r
        video_db_ischange = common.getSysKV('video_db_ischange')
        if video_db_ischange == '0':
            common.setSysKV('video_db_ischange', '1')

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
        action = request.form.get('action', '').encode('utf-8')

        vlist = common.M('video', 'video').where('id=?', vid).select()
        if len(vlist) < 1:
            return common.retFail('video doesn\'t exist, maybe syncing data...!!!')

        nlist = common.M('node').field(
            'id,info,port,name,ip').where('name=?', (mark,)).select()
        if len(nlist) < 1:
            return common.retFail('node info doesn\'t exist, maybe syncing data...!!!')

        rlist = common.M('task').where('vid=? and action=?',
                                       (vid, action)).limit('1').select()
        if len(rlist) > 0:
            return common.retFail('the task already exists...!!!', None, 2)
        # print()
        url = nlist[0]['ip'] + ':' + nlist[0]['port']
        sign = 'from:' + url
        r = common.M('task').add("ismaster,sign,vid,action,mark,status,uptime,addtime",
                                 (0, sign, vid, action, mark, 0, common.getDate(), common.getDate()))
        if not r:
            return common.retFail('the task add fail...!!!')
        return common.retOk()

    def asyncTaskApi(self):
        '''
        由主服务器发送请求,从服务器同步任务
        '''
        r = self.isNameRight()
        if r != '':
            return r

        mark = request.form.get('mark', '').encode('utf-8')
        vid = request.form.get('vid', '').encode('utf-8')
        action = request.form.get('action', '').encode('utf-8')

        vlist = common.M('video', 'video').where('id=?', vid).select()
        if len(vlist) < 1:
            return common.retFail('video doesn\'t exist, maybe syncing data...!!!')

        nlist = common.M('node').field(
            'id,info,port,name,ip').where('name=?', (mark,)).select()
        if len(nlist) < 1:
            return common.retFail('node info doesn\'t exist, maybe syncing data...!!!')

        rlist = common.M('task').where('vid=? and action=?',
                                       (vid, action)).limit('1').select()
        if len(rlist) > 0:
            return common.retFail('the task already exists...!!!', None, 2)
        # print()
        url = nlist[0]['ip'] + ':' + nlist[0]['port']
        sign = 'from:' + url
        r = common.M('task').add("ismaster,sign,vid,action,mark,status,uptime,addtime",
                                 (0, sign, vid, action, mark, 0, common.getDate(), common.getDate()))
        if not r:
            return common.retFail('the task add fail...!!!')
        return common.retOk()
