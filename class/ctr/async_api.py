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

    def nodeApi(self):

        sign = request.form.get('sign', '').encode('utf-8')
        source = request.form.get('source', '').encode('utf-8')

        _ret = {}
        _ret['code'] = 0
        _ret['sign'] = sign
        _ret['source'] = source
        _ret['msg'] = '成功'
        return common.getJson(_ret)
