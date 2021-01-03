# coding: utf-8

import psutil
import time
import os
import sys
import re
import json
import pwd

from flask import session
from flask import request

from werkzeug.utils import secure_filename
from flask import send_from_directory

sys.path.append(os.getcwd() + "/class/core")
import common


class video_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###
    def uploadApi(self):
        file = request.files['file']
        print(file)
        filename = file.filename

        # r = send_from_directory(
        # '/Users/midoks/go/src/github.com/midoks/vms/test', filename)

        r = file.save(os.path.join(
            '/Users/midoks/go/src/github.com/midoks/vms/tmp', filename))

        print('rrr:', r)
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = 'ok'

        return common.getJson(_ret)

    def indexApi(self):
        _ret = {}

        limit = request.form.get('limit', '10').encode('utf-8')
        p = request.form.get('p', '1').encode('utf-8')

        start = (int(p) - 1) * (int(limit))

        videoM = common.M('video')
        _list = videoM.field('id,name,size,status,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        count = videoM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)
