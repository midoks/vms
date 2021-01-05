#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

# unalias cp
# alias cp='cp -i'

if [ -d /tmp/vms-main ];then
    rm -rf /tmp/vms-main
fi

if [ -f /tmp/main.zip ];then
    rm -rf /tmp/main.zip
fi

wget -O /tmp/main.zip https://codeload.github.com/midoks/vms/zip/main
cd /tmp && unzip /tmp/main.zip

rm -rf /www/wwwroot/vms/*.pyc

pip install -r /www/wwwroot/vms/requirements.txt


/usr/bin/cp -rf  /tmp/vms-main/* /www/wwwroot/vms

cd /www/wwwroot/vms && service vms restart
cd /www/wwwroot/vms && ./scripts/init.d/vms default