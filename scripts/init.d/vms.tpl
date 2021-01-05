#!/bin/bash
# chkconfig: 2345 55 25
# description: VMS Cloud Service

### BEGIN INIT INFO
# Provides:          bt
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts vms
# Description:       starts the vms
### END INIT INFO


PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
app_path={$SERVER_PATH}

mw_start(){
	isStart=`ps -ef|grep 'gunicorn -c setting.py vms:app' |grep -v grep|awk '{print $2}'`
	if [ "$isStart" == '' ];then
            echo -e "Starting vms... \c"
            cd $app_path && gunicorn -c setting.py vms:app
            port=$(cat ${app_path}/data/port.pl)
            isStart=""
            while [[ "$isStart" == "" ]];
            do
                echo -e ".\c"
                sleep 0.5
                isStart=$(lsof -n -P -i:$port|grep LISTEN|grep -v grep|awk '{print $2}'|xargs)
                let n+=1
                if [ $n -gt 15 ];then
                    break;
                fi
            done
            if [ "$isStart" == '' ];then
                    echo -e "\033[31mfailed\033[0m"
                    echo '------------------------------------------------------'
                    tail -n 20 ${app_path}/logs/error.log
                    echo '------------------------------------------------------'
                    echo -e "\033[31mError: vms service startup failed.\033[0m"
                    return;
            fi
            echo -e "\033[32mdone\033[0m"
    else
            echo "Starting vms... mw(pid $(echo $isStart)) already running"
    fi


    isStart=$(ps aux |grep 'vms_task.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
            echo -e "Starting vms-tasks... \c"
            cd $app_path && nohup python vms_task.py >> $app_path/logs/task.log 2>&1 &
            sleep 0.3
            isStart=$(ps aux |grep 'vms_task.py'|grep -v grep|awk '{print $2}')
            if [ "$isStart" == '' ];then
                    echo -e "\033[31mfailed\033[0m"
                    echo '------------------------------------------------------'
                    tail -n 20 $app_path/logs/task.log
                    echo '------------------------------------------------------'
                    echo -e "\033[31mError: vms-tasks service startup failed.\033[0m"
                    return;
            fi
            echo -e "\033[32mdone\033[0m"
    else
            echo "Starting vms-tasks... vms-tasks (pid $isStart) already running"
    fi


    isStart=$(ps aux |grep 'vms_async.py'|grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
            echo -e "Starting vms-async... \c"
            cd $app_path && nohup python vms_async.py >> $app_path/logs/vms_async.log 2>&1 &
            sleep 0.3
            isStart=$(ps aux |grep 'vms_async.py'|grep -v grep|awk '{print $2}')
            if [ "$isStart" == '' ];then
                    echo -e "\033[31mfailed\033[0m"
                    echo '------------------------------------------------------'
                    tail -n 20 $app_path/logs/task.log
                    echo '------------------------------------------------------'
                    echo -e "\033[31mError: vms-async service startup failed.\033[0m"
                    return;
            fi
            echo -e "\033[32mdone\033[0m"
    else
            echo "Starting vms-async... vms-async (pid $isStart) already running"
    fi
}


mw_stop()
{
    echo -e "Stopping vms-async... \c";
    pids=$(ps aux | grep 'vms_async.py'|grep -v grep|awk '{print $2}')
    for p in ${arr[@]}
    do
            kill -9 $p &>/dev/null
    done
    
    if [ -f $pidfile ];then
        rm -f $pidfile
    fi
    echo -e "\033[32mdone\033[0m"


	echo -e "Stopping vms-tasks... \c";
    pids=$(ps aux | grep 'vms_task.py'|grep -v grep|awk '{print $2}')
    arr=($pids)

    for p in ${arr[@]}
    do
            kill -9 $p
    done
    echo -e "\033[32mdone\033[0m"

    echo -e "Stopping vms... \c";
    arr=`ps aux|grep 'gunicorn -c setting.py vms:app'|grep -v grep|awk '{print $2}'`
	for p in ${arr[@]}
    do
            kill -9 $p &>/dev/null
    done
    
    if [ -f $pidfile ];then
    	rm -f $pidfile
    fi
    echo -e "\033[32mdone\033[0m"

}

mw_status()
{
        isStart=$(ps aux|grep 'gunicorn -c setting.py app:app'|grep -v grep|awk '{print $2}')
        if [ "$isStart" != '' ];then
                echo -e "\033[32mvms (pid $(echo $isStart)) already running\033[0m"
        else
                echo -e "\033[31mvms not running\033[0m"
        fi
        
        isStart=$(ps aux |grep 'task.py'|grep -v grep|awk '{print $2}')
        if [ "$isStart" != '' ];then
                echo -e "\033[32mvms-task (pid $isStart) already running\033[0m"
        else
                echo -e "\033[31mvms-task not running\033[0m"
        fi
}


mw_reload()
{
	isStart=$(ps aux|grep 'gunicorn -c setting.py vms:app'|grep -v grep|awk '{print $2}')
    
    if [ "$isStart" != '' ];then
    	echo -e "Reload mw... \c";
	    arr=`ps aux|grep 'gunicorn -c setting.py vms:app'|grep -v grep|awk '{print $2}'`
		for p in ${arr[@]}
        do
                kill -9 $p
        done
        cd $app_path && gunicorn -c setting.py vms:app
        isStart=`ps aux|grep 'gunicorn -c setting.py vms:app'|grep -v grep|awk '{print $2}'`
        if [ "$isStart" == '' ];then
                echo -e "\033[31mfailed\033[0m"
                echo '------------------------------------------------------'
                tail -n 20 $app_path/logs/error.log
                echo '------------------------------------------------------'
                echo -e "\033[31mError: vms service startup failed.\033[0m"
                return;
        fi
        echo -e "\033[32mdone\033[0m"
    else
        echo -e "\033[31mvms not running\033[0m"
        mw_start
    fi
}


error_logs()
{
	tail -n 100 $app_path/logs/error.log
}

case "$1" in
    'start') mw_start;;
    'stop') mw_stop;;
    'reload') mw_reload;;
    'restart') 
        mw_stop
        mw_start;;
    'status') mw_status;;
    'logs') error_logs;;
    'default')
        cd $app_path
        port=$(cat $app_path/data/port.pl)
        password=$(cat $app_path/data/default.pl)
        if [ -f $app_path/data/domain.conf ];then
            address=$(cat $app_path/data/domain.conf)
        fi
        if [ -f $app_path/data/admin_path.pl ];then
            auth_path=$(cat $app_path/data/admin_path.pl)
        fi

        if [ "$address" = "" ];then
            address=$(curl -sS --connect-timeout 10 -m 60 https://www.bt.cn/Api/getIpAddress)
        fi

        echo -e "=================================================================="
        echo -e "\033[32mVMS default info!\033[0m"
        echo -e "=================================================================="
        echo  "VMS-URL: http://$address:$port$auth_path"
        echo -e "=================================================================="
        echo -e "username: admin"
        echo -e "password: $password"
        ;;
esac