#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/usr/local/lib/python2.7/bin



mvg_start(){
	gunicorn -c setting.py app:vms
	python vms_task.py &
}


mvg_start_debug(){
	# python vms_task.py &
	gunicorn -b :7200 -k gevent -w 1 app:app
}

mvg_stop()
{
	PLIST=`ps -ef|grep app:vms |grep -v grep|awk '{print $2}'`
	for i in $PLIST
	do
	    kill -9 $i
	done
	ps -ef|grep vms_task.py |grep -v grep|awk '{print $2}'|xargs kill -9
}

case "$1" in
    'start') mvg_start;;
    'stop') mvg_stop;;
    'restart') 
		mvg_stop 
		mvg_start
		;;
	'debug') 
		mvg_stop 
		mvg_start_debug
		;;
esac