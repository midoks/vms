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

sys.path.append(os.getcwd() + "/class/core")
import common


class video_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###

    def indexApi(self):
        _ret = {}

        limit = request.form.get('limit', '10').encode('utf-8')
        p = request.form.get('p', '1').encode('utf-8')

        start = (int(p) - 1) * (int(limit))

        videoM = common.M('video')
        _list = videoM.field('id,name,status,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        _page = {}
        _page['count'] = 0
        _page['tojs'] = 'getWeb'
        _page['p'] = p
        _page['row'] = limit

        # _ret['page'] = common.getPage(_page)

        _ret['data'] = _list
        _ret['code'] = 0

        return common.getJson(_ret)
