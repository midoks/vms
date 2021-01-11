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


class async_api:

    def __init__(self):
        pass

    def isNameRight(self):
        name = request.form.get('name', '0').encode('utf-8')
        mark = common.getSysKV('run_mark')
        if name != mark:
            return common.retFail('name is error!')
        return ''

    def nodeApi(self):
        import json
        r = self.isNameRight()
        if r != '':
            return r

        source = request.form.get('source').encode('utf-8')
        source = source.replace("'", '"').replace("u", '')

        rr = json.loads(source)
        nodeM = common.M('node')

        retList = nodeM.field('id,name,ip,port,ismaster').where(
            'name<>?', (rr['name'],)).select()
        if len(retList) > 100:
            return common.retFail('too many nodes!')

        dataList = nodeM.field('id,name,ip,port,ismaster').where(
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
        dsize = os.path.getsize('data/video.db')
        return common.retOk('ok', dsize)

    def videoRangeApi(self):

        start = request.form.get('start', '0').encode('utf-8')
        slen = request.form.get('slen', '1024').encode('utf-8')
        c = common.readFilePos('data/video.db', start, slen)
        return common.retOk('ok', base64.b64encode(c))
