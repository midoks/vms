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

reload(sys)
sys.setdefaultencoding('utf-8')


class node_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###

    def indexApi(self):
        _ret = {}

        limit = request.form.get('limit', '10').encode('utf-8')
        p = request.form.get('p', '1').encode('utf-8')

        start = (int(p) - 1) * (int(limit))

        nodeM = common.M('node')
        _list = nodeM.field('id,name,ip,port,ismaster,uptime,addtime').limit(
            (str(start)) + ',' + limit).order('id desc').select()

        count = nodeM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)

    def getApi(self):
        sid = request.args.get('id', '').encode('utf-8')
        videoM = common.M('node')
        _list = videoM.field('id,name,ip,port,ismaster,uptime,addtime').where(
            'id=?', (sid,)).select()
        _ret = {}
        _ret['data'] = _list
        _ret['code'] = 0

        return common.getJson(_ret)

    def editApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        name = request.form.get('name', '').encode('utf-8')
        ip = request.form.get('ip', '').encode('utf-8')
        port = request.form.get('port', '').encode('utf-8')

        nodeM = common.M('node')

        _ret = {}
        if sid:
            nodeM.where('id=?', (sid,)).save('name,ip,port', (name, ip, port))
            _ret['code'] = 0
            _ret['msg'] = '修改成功'
        else:
            r = nodeM.add("name,type,ip,port,uptime,addtime",
                          (name, 0, ip, port, common.getDate(), common.getDate()))

            _ret['code'] = 0
            _ret['msg'] = '添加成功'
            if not r:
                _ret['code'] = 1
                _ret['msg'] = '添加失败'

        return common.getJson(_ret)

    def delApi(self):

        sid = request.form.get('id', '').encode('utf-8')

        nodeM = common.M('node')
        r = nodeM.where("id=?", (sid,)).delete()
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '删除成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '删除失败'

        return common.getJson(_ret)

    def clearApi(self):

        common.M('node').delete()
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '清空成功'
        return common.getJson(_ret)
