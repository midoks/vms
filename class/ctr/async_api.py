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

reload(sys)
sys.setdefaultencoding('utf-8')

from flask import session
from flask import request

from werkzeug.utils import secure_filename
from flask import send_from_directory

sys.path.append(os.getcwd() + "/class/core")
import common


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
        dataList = nodeM.where('name=?', (rr['name'])).select()
        if len(dataList) > 0:

            rAdd = nodeM.add("name,ip,port,ismaster,uptime,addtime", (rr['name'], rr[
                'ip'], rr['port'], rr['ismaster'], common.getDate(), common.getDate()))

            if rAdd:
                return common.retOk()
            return common.retFail()
        else:
            return common.retOk('already exists!')
