#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

mkdir -p /www/wwwroot



yum install -y libevent libevent-devel mysql-devel libjpeg* libpng* gd* zip unzip

if [ ! -d /www/wwwroot/vms ];then
	wget -O /tmp/master.zip https://codeload.github.com/midoks/vms/zip/master
	cd /tmp && unzip /tmp/main.zip
	mv /tmp/vms-main /www/wwwroot/vms
	rm -rf /tmp/main.zip
	rm -rf /tmp/vms-main
fi 

yum groupinstall -y "Development Tools"
paces="wget python-devel python-imaging libicu-devel zip unzip bzip2-devel gcc libxml2 libxml2-dev libxslt* libjpeg-devel libpng-devel libwebp libwebp-devel lsof pcre pcre-devel vixie-cron crontabs"
yum -y install $paces
yum -y lsof net-tools.x86_64
yum -y install ncurses-devel mysql-dev locate cmake
yum -y install python-devel.x86_64
yum -y install MySQL-python 
yum -y install epel-release

if [ ! -f '/usr/bin/pip' ];then
	wget https://bootstrap.pypa.io/get-pip.py
	python get-pip.py
	pip install --upgrade pip
fi 



pip install -r /www/wwwroot/vms/requirements.txt


cd /www/wwwroot/vms && ./cli.sh start
sleep 5

cd /www/wwwroot/vms && ./cli.sh stop
cd /www/wwwroot/vms && ./scripts/init.d/vms default
cd /www/wwwroot/vms && ./cli.sh start