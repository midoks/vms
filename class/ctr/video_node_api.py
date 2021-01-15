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


class video_node_api:

    def __init__(self):
        pass

    def indexApi(self):
        _ret = {}

        pid = request.args.get('id', '').encode('utf-8')
        limit = request.args.get('limit', '10').encode('utf-8')
        p = request.args.get('p', '1').encode('utf-8')
        # print(pid, limit, p)

        start = (int(p) - 1) * (int(limit))

        videoM = common.M('video_node', 'video')
        _list = videoM.field('id,pid,node_id,addtime').where(
            'pid=?', (pid,)).select()

        for x in xrange(0, len(_list)):
            if _list[x]['node_id'] == common.getSysKV('run_mark'):
                _list[x]['node_id'] = _list[x]['node_id'] + '[本地]'
            else:
                _list[x]['node_id'] = _list[x]['node_id'] + '[从服务器]'

        count = videoM.count()

        _ret['data'] = _list
        _ret['count'] = count
        _ret['code'] = 0

        return common.getJson(_ret)

    def getApi(self):
        sid = request.args.get('id', '').encode('utf-8')
        videoM = common.M('video_node', 'video')
        _list = videoM.field('id,pid,node_id,addtime').where(
            'id=?', (sid,)).select()
        _ret = {}
        _ret['data'] = _list
        _ret['code'] = 0

        return common.getJson(_ret)

    def delApi(self):
        sid = request.form.get('id', '').encode('utf-8')
        videoM = common.M('video_node', 'video')

        data = videoM.field('id').where('id=?', (sid,)).select()

        r = videoM.where("id=?", (sid,)).delete()
        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '删除成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '删除失败'

        return common.getJson(_ret)
