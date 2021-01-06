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

        if not data:
            _ret['code'] = 1
            _ret['msg'] = '登陆失败'
        return common.getJson(_ret)

    def editApi(self):
        username = request.form.get('username', '').encode('utf-8')
        password = request.form.get('password', '').encode('utf-8')
        email = request.form.get('email', '').encode('utf-8')
        userM = common.M('users')

        if len(password) != 32:
            password = common.md5(password)

        r = userM.where('id=?', (1,)).save(
            'username,password,email', (username, password, email,))

        _ret = {}
        _ret['code'] = 0
        _ret['msg'] = '修改成功'
        if not r:
            _ret['code'] = 1
            _ret['msg'] = '修改失败'

        return common.getJson(_ret)

    def getApi(self):
        sid = request.args.get('id', '').encode('utf-8')
        userM = common.M('users')
        _list = userM.field('id,username,password,email').where(
            'id=?', (1,)).select()
        _ret = {}
        _ret['data'] = _list
        _ret['code'] = 0
        return common.getJson(_ret)
