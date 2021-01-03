# coding: utf-8

import psutil
import time
import os
import sys
import re
import json
import pwd
import hashlib

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
        filename = file.filename

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
        _list = videoM.field('id,name,size,status,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        count = videoM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)