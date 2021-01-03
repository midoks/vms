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


class api_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###

    def indexApi(self):
        _ret = {}

        limit = request.form.get('limit', '10').encode('utf-8')
        p = request.form.get('p', '1').encode('utf-8')

        start = (int(p) - 1) * (int(limit))

        apiM = common.M('api')
        _list = apiM.field('id,appkey,appsecret,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        count = apiM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)

    def delApi(self):

        sid = request.form.get('id', '').encode('utf-8')

        apiM = common.M('api')
        r = apiM.where("id=?", (sid,)).delete()
        # print(sid, r)
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '删除成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '删除失败'

        return common.getJson(_ret)

    def addApi(self):
        appkey = request.form.get('appkey', '').encode('utf-8')
        appsecret = request.form.get('appsecret', '').encode('utf-8')

        apiM = common.M('api')
        r = apiM.add("appkey,appsecret,addtime",
                     (appkey, appsecret, common.getDate()))

        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '添加成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '添加失败'

        return common.getJson(_ret)
