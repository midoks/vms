# coding: utf-8

import os
import sys
import time
import string
import json
import hashlib
import shlex
import datetime
import subprocess
import re
import hashlib
from random import Random
from flask import redirect

import db


def execShell(cmdstring, cwd=None, timeout=None, shell=True):

    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,
                           shell=shell, bufsize=4096, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout：%s" % cmdstring)

    return sub.communicate()


def getRunDir():
    return os.getcwd()


def getRootDir():
    return os.path.dirname(os.path.dirname(getRunDir()))


def getPluginDir():
    return getRunDir() + '/plugins'


def getServerDir():
    return getRootDir() + '/server'


def getWwwDir():
    file = getRunDir() + '/data/site.pl'
    if os.path.exists(file):
        return readFile(file).strip()
    return getRootDir() + '/wwwroot'


def setWwwDir(wdir):
    file = getRunDir() + '/data/site.pl'
    return writeFile(file, wdir)


def getLogsDir():
    return getRootDir() + '/wwwlogs'


def getBackupDir():
    return getRootDir() + '/backup'


def setBackupDir(bdir):
    file = getRunDir() + '/data/backup.pl'
    return writeFile(file, bdir)


def getOs():
    return sys.platform


def isAppleSystem():
    if getOs() == 'darwin':
        return True
    return False


def deleteFile(file):
    if os.path.exists(file):
        os.remove(file)


def isInstalledWeb():
    path = getServerDir() + '/openresty/nginx/sbin/nginx'
    if os.path.exists(path):
        return True
    return False


def restartWeb():
    if isInstalledWeb():
        initd = getServerDir() + '/openresty/init.d/openresty'
        execShell(initd + ' ' + 'reload')


def restartMw():
    import system_api
    system_api.system_api().restartMw()


def checkWebConfig():
    op_dir = getServerDir() + '/openresty'
    cmd = "ulimit -n 10240 && " + op_dir + \
        "/nginx/sbin/nginx -t -c " + op_dir + "/nginx/conf/nginx.conf"
    result = execShell(cmd)
    searchStr = 'successful'
    if result[1].find(searchStr) == -1:
        msg = getInfo('配置文件错误: {1}', (result[1],))
        writeLog("软件管理", msg)
        return result[1]
    return True


def M(table):
    sql = db.Sql()
    return sql.table(table)


def getPage(args, result='1,2,3,4,5,8'):
    data = getPageObject(args, result)
    return data[0]


def getPageObject(args, result='1,2,3,4,5,8'):
    # 取分页
    import page
    # 实例化分页类
    page = page.Page()
    info = {}

    info['count'] = 0
    if args.has_key('count'):
        info['count'] = int(args['count'])

    info['row'] = 10
    if args.has_key('row'):
        info['row'] = int(args['row'])

    info['p'] = 1
    if args.has_key('p'):
        info['p'] = int(args['p'])
    info['uri'] = {}
    info['return_js'] = ''
    if args.has_key('tojs'):
        info['return_js'] = args['tojs']

    return (page.GetPage(info, result), page)


def md5(str):
    # 生成MD5
    try:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    except:
        return False


def getFileMd5(filename):
    # 文件的MD5值
    if not os.path.isfile(filename):
        return False

    myhash = hashlib.md5()
    f = file(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def getRandomString(length):
    # 取随机字符串
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    chrlen = len(chars) - 1
    random = Random()
    for i in range(length):
        str += chars[random.randint(0, chrlen)]
    return str


def getJson(data):
    import json
    return json.dumps(data)


def returnData(status, msg, data=None):
    return {'status': status, 'msg': msg, 'data': data}


def returnJson(status, msg, data=None):
    # if data == None:
    #     return {'status': status, 'msg': msg}
    # return {'status': status, 'msg': msg, 'data': data}
    if data == None:
        return getJson({'status': status, 'msg': msg})
    return getJson({'status': status, 'msg': msg, 'data': data})


def returnMsg(status, msg, args=()):
    # 取通用字曲返回
    pjson = 'static/language/' + getLanguage() + '/public.json'
    logMessage = json.loads(readFile(pjson))
    keys = logMessage.keys()

    if msg in keys:
        msg = logMessage[msg]
        for i in range(len(args)):
            rep = '{' + str(i + 1) + '}'
            msg = msg.replace(rep, args[i])
    return {'status': status, 'msg': msg, 'data': args}


def getInfo(msg, args=()):
    # 取提示消息
    for i in range(len(args)):
        rep = '{' + str(i + 1) + '}'
        msg = msg.replace(rep, args[i])
    return msg


def getMsg(key, args=()):
    # 取提示消息
    try:
        logMessage = json.loads(
            readFile('static/language/' + getLanguage() + '/public.json'))
        keys = logMessage.keys()
        msg = None
        if key in keys:
            msg = logMessage[key]
            for i in range(len(args)):
                rep = '{' + str(i + 1) + '}'
                msg = msg.replace(rep, args[i])
        return msg
    except:
        return key


def getLan(key):
    # 取提示消息
    logMessage = json.loads(
        readFile('static/language/' + getLanguage() + '/template.json'))
    keys = logMessage.keys()
    msg = None
    if key in keys:
        msg = logMessage[key]
    return msg


def readFile(filename):
    # 读文件内容
    try:
        fp = open(filename, 'r')
        fBody = fp.read()
        fp.close()
        return fBody
    except:
        return False


def getDate():
    # 取格式时间
    import time
    return time.strftime('%Y-%m-%d %X', time.localtime())


def getLanguage():
    path = 'data/language.pl'
    if not os.path.exists(path):
        return 'Simplified_Chinese'
    return readFile(path).strip()


def writeLog(type, logMsg, args=()):
    # 写日志
    try:
        import time
        import db
        import json
        sql = db.Sql()
        mDate = time.strftime('%Y-%m-%d %X', time.localtime())
        data = (type, logMsg, mDate)
        result = sql.table('logs').add('type,log,addtime', data)
    except Exception as e:
        print e


def writeFile(filename, str):
    # 写文件内容
    try:
        fp = open(filename, 'w+')
        fp.write(str)
        fp.close()
        return True
    except:
        return False


def HttpGet(url, timeout=10):
    """
    发送GET请求
    @url 被请求的URL地址(必需)
    @timeout 超时时间默认60秒
    return string
    """
    if sys.version_info[0] == 2:
        try:
            import urllib2
            import ssl
            if sys.version_info[0] == 2:
                reload(urllib2)
                reload(ssl)
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            response = urllib2.urlopen(url, timeout=timeout)
            return response.read()
        except Exception as ex:
            return str(ex)
    else:
        try:
            import urllib.request
            import ssl
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            response = urllib.request.urlopen(url, timeout=timeout)
            result = response.read()
            if type(result) == bytes:
                result = result.decode('utf-8')
            return result
        except Exception as ex:
            return str(ex)


def HttpGet2(url, timeout):
    import urllib2

    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req, timeout=timeout)
        result = res.read()
        return result

    except Exception as e:
        return str(e)


def httpGet(url, timeout=10):
    return HttpGet2(url, timeout)


def HttpPost(url, data, timeout=10):
    """
    发送POST请求
    @url 被请求的URL地址(必需)
    @data POST参数，可以是字符串或字典(必需)
    @timeout 超时时间默认60秒
    return string
    """
    if sys.version_info[0] == 2:
        try:
            import urllib
            import urllib2
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req, timeout=timeout)
            return response.read()
        except Exception as ex:
            return str(ex)
    else:
        try:
            import urllib.request
            import ssl
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(url, data)
            response = urllib.request.urlopen(req, timeout=timeout)
            result = response.read()
            if type(result) == bytes:
                result = result.decode('utf-8')
            return result
        except Exception as ex:
            return str(ex)


def httpPost(url, data, timeout=10):
    return HttpPost(url, data, timeout)


def writeSpeed(title, used, total, speed=0):
    # 写进度
    if not title:
        data = {'title': None, 'progress': 0,
                'total': 0, 'used': 0, 'speed': 0}
    else:
        progress = int((100.0 * used / total))
        data = {'title': title, 'progress': progress,
                'total': total, 'used': used, 'speed': speed}
    writeFile('/tmp/panelSpeed.pl', json.dumps(data))
    return True


def getSpeed():
    # 取进度
    path = getRootDir()
    data = readFile(path + '/tmp/panelSpeed.pl')
    if not data:
        data = json.dumps({'title': None, 'progress': 0,
                           'total': 0, 'used': 0, 'speed': 0})
        writeFile(path + '/tmp/panelSpeed.pl', data)
    return json.loads(data)


def getLastLine(inputfile, lineNum):
    # 读文件指定倒数行数
    try:
        fp = open(inputfile, 'r')
        lastLine = ""

        lines = fp.readlines()
        count = len(lines)
        if count > lineNum:
            num = lineNum
        else:
            num = count
        i = 1
        lastre = []
        for i in range(1, (num + 1)):
            if lines:
                n = -i
                lastLine = lines[n].strip()
                fp.close()
                lastre.append(lastLine)

        result = ''
        num -= 1
        while num >= 0:
            result += lastre[num] + "\n"
            num -= 1
        return result
    except:
        return getMsg('TASK_SLEEP')


def getNumLines(path, num, p=1):
    pyVersion = sys.version_info[0]
    try:
        import cgi
        if not os.path.exists(path):
            return ""
        start_line = (p - 1) * num
        count = start_line + num
        fp = open(path, 'rb')
        buf = ""
        fp.seek(-1, 2)
        if fp.read(1) == "\n":
            fp.seek(-1, 2)
        data = []
        b = True
        n = 0
        for i in range(count):
            while True:
                newline_pos = str.rfind(str(buf), "\n")
                pos = fp.tell()
                if newline_pos != -1:
                    if n >= start_line:
                        line = buf[newline_pos + 1:]
                        try:
                            data.insert(0, cgi.escape(line))
                        except:
                            pass
                    buf = buf[:newline_pos]
                    n += 1
                    break
                else:
                    if pos == 0:
                        b = False
                        break
                    to_read = min(4096, pos)
                    fp.seek(-to_read, 1)
                    t_buf = fp.read(to_read)
                    if pyVersion == 3:
                        if type(t_buf) == bytes:
                            t_buf = t_buf.decode('utf-8')
                    buf = t_buf + buf
                    fp.seek(-to_read, 1)
                    if pos - to_read == 0:
                        buf = "\n" + buf
            if not b:
                break
        fp.close()
    except Exception as e:
        return ''

    return "\n".join(data)


def downloadFile(url, filename):
    import urllib
    urllib.urlretrieve(url, filename=filename, reporthook=downloadHook)


def downloadHook(count, blockSize, totalSize):
    speed = {'total': totalSize, 'block': blockSize, 'count': count}
    print speed
    print '%02d%%' % (100.0 * count * blockSize / totalSize)


def getLocalIp():
    # 取本地外网IP
    try:
        import re
        filename = 'data/iplist.txt'
        ipaddress = readFile(filename)
        if not ipaddress:
            import urllib2
            url = 'http://pv.sohu.com/cityjson?ie=utf-8'
            opener = urllib2.urlopen(url)
            str = opener.read()
            ipaddress = re.search('\d+.\d+.\d+.\d+', str).group(0)
            writeFile(filename, ipaddress)

        ipaddress = re.search('\d+.\d+.\d+.\d+', ipaddress).group(0)
        return ipaddress
    except:
        return '127.0.0.1'


def inArray(arrays, searchStr):
    # 搜索数据中是否存在
    for key in arrays:
        if key == searchStr:
            return True

    return False


def checkIp(ip):
    # 检查是否为IPv4地址
    import re
    p = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False


def checkPort(port):
    # 检查端口是否合法
    ports = ['21', '25', '443', '7200', '8080', '888', '8888', '8443']
    if port in ports:
        return False
    intport = int(port)
    if intport < 1 or intport > 65535:
        return False
    return True


def getStrBetween(startStr, endStr, srcStr):
    # 字符串取中间
    start = srcStr.find(startStr)
    if start == -1:
        return None
    end = srcStr.find(endStr)
    if end == -1:
        return None
    return srcStr[start + 1:end]


def getCpuType():
    # 取CPU类型
    cpuinfo = open('/proc/cpuinfo', 'r').read()
    rep = "model\s+name\s+:\s+(.+)"
    tmp = re.search(rep, cpuinfo)
    cpuType = None
    if tmp:
        cpuType = tmp.groups()[0]
    return cpuType


def isRestart():
    # 检查是否允许重启
    num = M('tasks').where('status!=?', ('1',)).count()
    if num > 0:
        return False
    return True


def isUpdateLocalSoft():
    num = M('tasks').where('status!=?', ('1',)).count()
    if os.path.exists('mdserver-web.zip'):
        return True

    if num > 0:
        data = M('tasks').where('status!=?', ('1',)).field(
            'id,type,execstr').limit('1').select()
        argv = data[0]['execstr'].split('|dl|')
        if data[0]['type'] == 'download' and argv[1] == 'mdserver-web.zip':
            return True

    return False


def hasPwd(password):
    # 加密密码字符
    import crypt
    return crypt.crypt(password, password)


def getTimeout(url):
    start = time.time()
    result = httpGet(url)
    if result != 'True':
        return False
    return int((time.time() - start) * 1000)


def makeConf():
    file = getRunDir() + '/data/json/config.json'
    if not os.path.exists(file):
        c = {}
        c['title'] = 'Linux面板'
        c['home'] = 'http://github/midoks/mdserver-web'
        c['recycle_bin'] = True
        c['template'] = 'default'
        writeFile(file, json.dumps(c))
        return c
    c = readFile(file)
    return json.loads(c)


def getConfig(k):
    c = makeConf()
    return c[k]


def setConfig(k, v):
    c = makeConf()
    c[k] = v
    file = getRunDir() + '/data/json/config.json'
    return writeFile(file, json.dumps(c))


def getHostAddr():
    if os.path.exists('data/iplist.txt'):
        return readFile('data/iplist.txt').strip()
    return '127.0.0.1'


def setHostAddr(addr):
    file = getRunDir() + '/data/iplist.txt'
    return writeFile(file, addr)


def getHostPort():
    if os.path.exists('data/port.pl'):
        return readFile('data/port.pl').strip()
    return '7200'


def setHostPort(port):
    file = getRunDir() + '/data/port.pl'
    return writeFile(file, port)


def auth_decode(data):
    # 解密数据
    token = GetToken()
    # 是否有生成Token
    if not token:
        return returnMsg(False, 'REQUEST_ERR')

    # 校验access_key是否正确
    if token['access_key'] != data['btauth_key']:
        return returnMsg(False, 'REQUEST_ERR')

    # 解码数据
    import binascii
    import hashlib
    import urllib
    import hmac
    import json
    tdata = binascii.unhexlify(data['data'])

    # 校验signature是否正确
    signature = binascii.hexlify(
        hmac.new(token['secret_key'], tdata, digestmod=hashlib.sha256).digest())
    if signature != data['signature']:
        return returnMsg(False, 'REQUEST_ERR')

    # 返回
    return json.loads(urllib.unquote(tdata))


# 数据加密
def auth_encode(data):
    token = GetToken()
    pdata = {}

    # 是否有生成Token
    if not token:
        return returnMsg(False, 'REQUEST_ERR')

    # 生成signature
    import binascii
    import hashlib
    import urllib
    import hmac
    import json
    tdata = urllib.quote(json.dumps(data))
    # 公式  hex(hmac_sha256(data))
    pdata['signature'] = binascii.hexlify(
        hmac.new(token['secret_key'], tdata, digestmod=hashlib.sha256).digest())

    # 加密数据
    pdata['btauth_key'] = token['access_key']
    pdata['data'] = binascii.hexlify(tdata)
    pdata['timestamp'] = time.time()

    # 返回
    return pdata


def checkToken(get):
    # 检查Token
    tempFile = 'data/tempToken.json'
    if not os.path.exists(tempFile):
        return False
    import json
    import time
    tempToken = json.loads(readFile(tempFile))
    if time.time() > tempToken['timeout']:
        return False
    if get.token != tempToken['token']:
        return False
    return True


def checkInput(data):
    # 过滤输入
    if not data:
        return data
    if type(data) != str:
        return data
    checkList = [
        {'d': '<', 'r': '＜'},
        {'d': '>', 'r': '＞'},
        {'d': '\'', 'r': '‘'},
        {'d': '"', 'r': '“'},
        {'d': '&', 'r': '＆'},
        {'d': '#', 'r': '＃'},
        {'d': '<', 'r': '＜'}
    ]
    for v in checkList:
        data = data.replace(v['d'], v['r'])
    return data


def checkCert(certPath='ssl/certificate.pem'):
    # 验证证书
    openssl = '/usr/local/openssl/bin/openssl'
    if not os.path.exists(openssl):
        openssl = 'openssl'
    certPem = readFile(certPath)
    s = "\n-----BEGIN CERTIFICATE-----"
    tmp = certPem.strip().split(s)
    for tmp1 in tmp:
        if tmp1.find('-----BEGIN CERTIFICATE-----') == -1:
            tmp1 = s + tmp1
        writeFile(certPath, tmp1)
        result = execShell(openssl + " x509 -in " +
                           certPath + " -noout -subject")
        if result[1].find('-bash:') != -1:
            return True
        if len(result[1]) > 2:
            return False
        if result[0].find('error:') != -1:
            return False
    return True


def getPathSize(path):
    # 取文件或目录大小
    if not os.path.exists(path):
        return 0
    if not os.path.isdir(path):
        return os.path.getsize(path)
    size_total = 0
    for nf in os.walk(path):
        for f in nf[2]:
            filename = nf[0] + '/' + f
            size_total += os.path.getsize(filename)
    return size_total


def toSize(size):
    # 字节单位转换
    d = ('b', 'KB', 'MB', 'GB', 'TB')
    s = d[0]
    for b in d:
        if size < 1024:
            return str(round(size, 2)) + ' ' + b
        size = float(size) / 1024.0
        s = b
    return str(round(size, 2)) + ' ' + b


def getMacAddress():
    # 获取mac
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def get_string(t):
    if t != -1:
        max = 126
        m_types = [{'m': 122, 'n': 97}, {'m': 90, 'n': 65}, {'m': 57, 'n': 48}, {
            'm': 47, 'n': 32}, {'m': 64, 'n': 58}, {'m': 96, 'n': 91}, {'m': 125, 'n': 123}]
    else:
        max = 256
        t = 0
        m_types = [{'m': 255, 'n': 0}]
    arr = []
    for i in range(max):
        if i < m_types[t]['n'] or i > m_types[t]['m']:
            continue
        arr.append(chr(i))
    return arr


def get_string_find(t):
    if type(t) != list:
        t = [t]
    return_str = ''
    for s1 in t:
        return_str += get_string(int(s1[0]))[int(s1[1:])]
    return return_str


def get_string_arr(t):
    s_arr = {}
    t_arr = []
    for s1 in t:
        for i in range(6):
            if not i in s_arr:
                s_arr[i] = get_string(i)
            for j in range(len(s_arr[i])):
                if s1 == s_arr[i][j]:
                    t_arr.append(str(i) + str(j))
    return t_arr


def getSSHPort():
    try:
        file = '/etc/ssh/sshd_config'
        conf = ReadFile(file)
        rep = "#*Port\s+([0-9]+)\s*\n"
        port = re.search(rep, conf).groups(0)[0]
        return int(port)
    except:
        return 22


def getSSHStatus():
    if os.path.exists('/usr/bin/apt-get'):
        status = execShell("service ssh status | grep -P '(dead|stop)'")
    else:
        import system_api
        version = system_api.system_api().getSystemVersion()
        if version.find(' Mac ') != -1:
            return True
        if version.find(' 7.') != -1:
            status = execShell("systemctl status sshd.service | grep 'dead'")
        else:
            status = execShell(
                "/etc/init.d/sshd status | grep -e 'stopped' -e '已停'")
    if len(status[0]) > 3:
        status = False
    else:
        status = True
    return status


def init():

    initDB()
    initInitD()
    # initUserInfo()


def local():
    result = checkClose()
    if result:
        return result


# 检查面板是否关闭
def checkClose():
    if os.path.exists('data/close.pl'):
        return redirect('/close')


def initDB():
    try:
        sql = db.Sql().dbfile('default')
        csql = readFile('data/sql/default.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            sql.execute(csql_list[index], ())

    except Exception, ex:
        print str(ex)


def initInitD():
    script = getRunDir() + '/scripts/init.d/vms.tpl'
    script_bin = getRunDir() + '/scripts/init.d/vms'
    if os.path.exists(script_bin):
        return

    print(script, script_bin)
    content = readFile(script)
    content = content.replace("{$SERVER_PATH}", getRunDir())

    writeFile(script_bin, content)
    execShell('chmod +x ' + script_bin)

    setHostAddr(getLocalIp())

    if not isAppleSystem():
        initd_bin = '/etc/init.d/vms'
        if not os.path.exists(initd_bin):
            import shutil
            shutil.copyfile(script_bin, initd_bin)
            execShell('chmod +x ' + initd_bin)
        # 加入自启动
        execShell('chkconfig --add vms')


def initUserInfo():
    data = M('users').where('id=?', (1,)).getField('password')
    if data == '21232f297a57a5a743894a0e4a801fc3':
        pwd = common.getRandomString(8).lower()
        file_pw = common.getRunDir() + '/data/default.pl'
        common.writeFile(file_pw, pwd)
        common.M('users').where('id=?', (1,)).setField(
            'password', common.md5(pwd))
