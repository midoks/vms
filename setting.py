# -- coding:utf-8 --


import time
import sys
import os
chdir = os.getcwd()
sys.path.append(chdir + '/class/core')
sys.path.append(chdir + '/class/ctr')
sys.path.append("/usr/local/lib/python2.7/site-packages")
import common
import system_api
cpu_info = system_api.system_api().getCpuInfo()
workers = cpu_info[1]

if not os.path.exists(os.getcwd() + '/logs'):
    os.mkdir(os.getcwd() + '/logs')

if not os.path.exists('data/port.pl'):
    common.writeFile('data/port.pl', '8000')

app_port = common.readFile('data/port.pl')
bind = []
if os.path.exists('data/ipv6.pl'):
    bind.append('[0:0:0:0:0:0:0:0]:%s' % app_port)
else:
    bind.append('0.0.0.0:%s' % app_port)

if workers > 2:
    workers = 2

threads = workers * 1
backlog = 512
reload = True
daemon = True
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
timeout = 7200
keepalive = 60
preload_app = True
capture_output = True
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
loglevel = 'info'
errorlog = chdir + '/logs/error.log'
accesslog = chdir + '/logs/access.log'
pidfile = chdir + '/logs/vms.pid'
