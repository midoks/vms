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


class user_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###
    def loginApi(self):
        _ret = {}

        username = request.form.get('username', '').encode('utf-8')
        password = request.form.get('password', '').encode('utf-8')

        _ret['code'] = 0
        _ret['msg'] = '登陆成功'
        userM = common.M('users')
        data = userM.field('id').where(
            'username=? and password=?', (username, common.md5(password),)).select()
        # print(username, password, data)
        # print(common.md5(password))

        if not data:
            _ret['code'] = 1
            _ret['msg'] = '登陆失败'
        return common.getJson(_ret)
