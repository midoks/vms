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
        name = request.form.get('name', '').encode('utf-8')
        mark = common.getSysKV('run_mark')
        if name != mark:
            return common.retFail('name is error!')
        return ''

    def nodeApi(self):
        r = self.isNameRight()
        if r != '':
            return r

        source = request.form.get('source', '').encode('utf-8')
        print source

        return common.retOk()
