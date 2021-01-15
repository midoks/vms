#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/usr/local/lib/python2.7/bin



mvg_start(){
	gunicorn -c setting.py vms:app
	python task/vms_task.py &
	python task/vms_async_master.py &
	python task/vms_async_slave.py &
	python task/vms_report.py &
}


mvg_start_debug(){
	# python vms_task.py &
	gunicorn -b :8000 -k gevent -w 1 vms:app
}

mvg_task_stop(){
	NAME="$1"
    FILE_NAME="$1.py"
	TLIST=`ps -ef|grep "$FILE_NAME" |grep -v grep|awk '{print $2}'`
	for i in $TLIST
	do
	    kill -9 $i
	done
}

mvg_stop()
{
	PLIST=`ps -ef|grep vms:app |grep -v grep|awk '{print $2}'`
	for i in $PLIST
	do
	    kill -9 $i
	done

	mvg_task_stop vms_task
	mvg_task_stop vms_async_master
	mvg_task_stop vms_async_slave
	mvg_task_stop vms_report
}

case "$1" in
    'start') mvg_start;;
    'stop') mvg_stop;;
    'restart') 
		mvg_stop 
		mvg_start
		;;
	'debug') 
		mvg_start_debug
		;;
esac