# coding:utf-8

import sys
import io
import os
import time
import shutil
import uuid

reload(sys)
sys.setdefaultencoding('utf-8')


from datetime import timedelta

from flask import Flask
from flask import render_template
from flask import make_response
from flask import Response
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask_caching import Cache
from flask_session import Session

sys.path.append(os.getcwd() + "/class/core")
sys.path.append(os.getcwd() + "/class/ctr")
sys.path.append("/usr/local/lib/python2.7/site-packages")

import common

app = Flask(__name__, template_folder='templates/default')
# app.config['UPLOAD_FOLDER'] = '/Users/midoks/go/src/github.com/midoks/vms/tmp'
# app.config.version = config_api.config_api().getVersion()
# app.config['SECRET_KEY'] = os.urandom(24)
# app.secret_key = uuid.UUID(int=uuid.getnode()).hex[-12:]
app.config['SECRET_KEY'] = uuid.UUID(int=uuid.getnode()).hex[-12:]
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

try:
    from flask_sqlalchemy import SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/mvg_session.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = sdb
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'session'
    sdb = SQLAlchemy(app)
    sdb.create_all()
except:
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/py_mvg_session_' + \
        str(sys.version_info[0])
    app.config['SESSION_FILE_THRESHOLD'] = 1024
    app.config['SESSION_FILE_MODE'] = 384
    # mw.execShell("pip install flask_sqlalchemy &")

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'mvg_:'
app.config['SESSION_COOKIE_NAME'] = "mvg_ver_1"
# Session(app)

# socketio
from flask_socketio import SocketIO, emit, send
socketio = SocketIO()
socketio.init_app(app)


common.init()


# 取数据对象
def get_input_data(data):
    pdata = common.dict_obj()
    for key in data.keys():
        pdata[key] = str(data[key])
    return pdata


def funConvert(fun):
    block = fun.split('_')
    func = block[0]
    for x in range(len(block) - 1):
        suf = block[x + 1].title()
        func += suf
    return func


def isLogined():
    if 'login' in session and 'username' in session and session['login'] == True:
        return True
    return False


def publicObject(toObject, func, action=None, get=None):
    name = funConvert(func) + 'Api'
    try:
        if hasattr(toObject, name):
            efunc = 'toObject.' + name + '()'
            data = eval(efunc)
            return data
    except Exception as e:
        data = {'code': -1, 'msg': '访问异常:' + str(e) + '!', "status": False}
        return common.getJson(data)


@app.before_request
def before_request():
    pass


@app.after_request
def apply_caching(response):
    response.headers["project_url"] = "https://github.com/midoks/vms"
    return response


@app.route("/test")
def test():
    print sys.version_info
    print session
    print os
    return 'test'


@app.route("/code")
def code():
    import vilidate
    vie = vilidate.vieCode()
    codeImage = vie.GetCodeImage(80, 4)
    try:
        from cStringIO import StringIO
    except:
        from StringIO import StringIO

    out = StringIO()
    codeImage[0].save(out, "png")

    session['code'] = common.md5(''.join(codeImage[1]).lower())

    img = Response(out.getvalue(), headers={'Content-Type': 'image/png'})
    return make_response(img)


@app.route("/check_login", methods=['POST'])
def checkLogin():
    if isLogined():
        return "true"
    return "false"


@app.route('/<reqClass>/<reqAction>', methods=['POST', 'GET'])
@app.route('/<reqClass>/', methods=['POST', 'GET'])
@app.route('/<reqClass>', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index(reqClass=None, reqAction=None, reqData=None):

    if reqClass == 'favicon.ico':
        return ''

    # print(reqClass, reqAction, reqData)
    if (reqClass == None):
        reqClass = 'index'
    classFile = ('config', 'index', 'user', 'system',
                 'node', 'video', 'video_node',
                 'api', 'logs', 'task', 'login', 'async', 'admin')

    if reqClass in classFile:
        import config_api
        data = config_api.config_api().get()
        if reqAction == None:
            return render_template(reqClass + '.html', data=data)
        else:
            return render_template(reqClass + '/' + reqAction + '.html', data=data)

    className = reqClass
    # print(className)
    eval_str = "__import__('" + className + "')." + className + '()'
    newInstance = eval(eval_str)
    # print(newInstance)
    return publicObject(newInstance, reqAction)


#from flask_cors import CORS
#CORS(app, resources=r'/m3u8/*')
@app.route('/v/<path>/<format>/<filename>', methods=['GET'])
def m3u8(path=None, format=None, filename=None):
    p = os.getcwd() + '/app/' + path + '/' + format + '/' + filename
    if os.path.exists(p):
        c = common.readFile(p)
        return c
    else:
        return 'not fund!'
