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


class logs_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###

    def indexApi(self):
        _ret = {}

        limit = request.form.get('limit', '10').encode('utf-8')
        p = request.form.get('p', '1').encode('utf-8')

        start = (int(p) - 1) * (int(limit))

        makeM = common.M('logs')
        _list = makeM.field('id,type,log,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        count = makeM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)

    def delApi(self):

        sid = request.get('id', '').encode('utf-8')

        makeM = common.M('logs')
        r = makeM.where("id=?", (sid,)).delete()
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '删除成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '删除失败'

        return common.getJson(_ret)

    def clearApi(self):

        common.M('logs').delete()
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '清空成功'
        return common.getJson(_ret)
