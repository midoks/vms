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


class config_api:

    __version = '0.0.1'

    def __init__(self):
        pass

    ##### ----- start ----- ###

    def v(self):
        return __version

    def getVersion(self):
        return self.__version

    def get(self):
        data = {}
        data['ip'] = common.getHostAddr()
        data['version'] = self.__version
        return data
