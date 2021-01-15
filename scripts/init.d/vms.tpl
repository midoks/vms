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


vms_task_start(){
    NAME="$1"
    FILE_NAME="$1.py"
    isStart=$(ps aux |grep "${FILE_NAME}" |grep -v grep|awk '{print $2}')
    if [ "$isStart" == '' ];then
            echo -e "Starting ${NAME}... \c"
            echo "" > $app_path/logs/${NAME}.log
            cd $app_path
            nohup python -u task/${NAME}.py >> $app_path/logs/${NAME}.log 2>&1 & 
            sleep 0.1
            isStart=$(ps aux |grep "${FILE_NAME}"|grep -v grep|awk '{print $2}')
            if [ "$isStart" == '' ];then
                    echo -e "\033[31mfailed\033[0m"
                    echo '------------------------------------------------------'
                    tail -n 20 $app_path/logs/${NAME}.log
                    echo '------------------------------------------------------'
                    echo -e "\033[31mError: ${NAME} service startup failed.\033[0m"
                    return;
            fi
            echo -e "\033[32mdone\033[0m"
    else
            echo "Starting ${NAME}... ${NAME} (pid $isStart) already running"
    fi
}


vms_task_stop()
{
    NAME="$1"
    FILE_NAME="$1.py"

    echo -e "Stopping ${NAME}... \c";
    arr=$(ps aux | grep "${NAME}" |grep -v grep|awk '{print $2}')
    for p in ${arr[@]}
    do
        kill -9 $p &>/dev/null
    done

    echo -e "\033[32mdone\033[0m"
}

vms_task_status()
{
    NAME="$1"
    FILE_NAME="$1.py"

    isStart=$(ps aux |grep "${FILE_NAME}" |grep -v grep|awk '{print $2}')
    if [ "$isStart" != '' ];then
            echo "\033[32m${NAME}(pid $isStart) already running\033[0m"
    else
            echo "\033[31m${NAME} not running\033[0m"
    fi
}


vms_start(){
	isStart=`ps -ef|grep 'vms:app' |grep -v grep|awk '{print $2}'`
    echo "" > $app_path/logs/error.log
	if [ "$isStart" == '' ];then
            echo -e "Starting vms... \c"
            cd $app_path && gunicorn -c setting.py vms:app
            port=$(cat ${app_path}/data/port.pl)
            isStart=""
            while [[ "$isStart" == "" ]];
            do
                echo -e ".\c"
                sleep 0.2
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
            echo "Starting vms... vms(pid $(echo $isStart)) already running"
    fi


    vms_task_start vms_task
    vms_task_start vms_report
    vms_task_start vms_async_master
}


vms_stop()
{
    vms_task_stop vms_task
    vms_task_stop vms_report
    vms_task_stop vms_async_master

    echo -e "Stopping vms... \c";
    arr=`ps aux|grep 'vms:app'|grep -v grep|awk '{print $2}'`
	for p in ${arr[@]}
    do
            kill -9 $p
    done
    
    if [ -f $pidfile ];then
    	rm -f $pidfile
    fi
    echo -e "\033[32mdone\033[0m"
}

vms_status()
{
        isStart=$(ps aux|grep 'gunicorn -c setting.py vms:app'|grep -v grep|awk '{print $2}')
        if [ "$isStart" != '' ];then
                echo -e "\033[32mvms (pid $(echo $isStart)) already running\033[0m"
        else
                echo -e "\033[31mvms not running\033[0m"
        fi
        
        vms_task_status vms_task
        vms_task_status vms_report
        vms_task_status vms_async_master
}


vms_reload()
{
	isStart=$(ps aux|grep 'vms:app'|grep -v grep|awk '{print $2}')
    
    if [ "$isStart" != '' ];then
    	echo -e "Reload vms... \c";
	    arr=`ps aux|grep 'vms:app'|grep -v grep|awk '{print $2}'`
		for p in ${arr[@]}
        do
                kill -9 $p
        done
        cd $app_path && gunicorn -c setting.py vms:app
        isStart=`ps aux|grep 'vms:app'|grep -v grep|awk '{print $2}'`
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
    'start') vms_start;;
    'stop') vms_stop;;
    'reload') vms_reload;;
    'restart') 
        vms_stop
        sleep 2
        vms_start;;
    'status') vms_status;;
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