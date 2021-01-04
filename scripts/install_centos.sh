#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

sysName=`uname`

mkdir -p /www/wwwroot
mkdir -p /www/server/lib

serverPath=/www/server

Install_mac_ffmpeg()
{
	macVer='ffmpeg-20200721-b5f1e05-macos64-static'
	if [ ! -f $serverPath/source/${macVer}.zip ];then
		wget -O $serverPath/source/${macVer}.zip https://ffmpeg.zeranoe.com/builds/macos64/static/${macVer}.zip
	fi

	if [ ! -d $serverPath/lib/ffmpeg ];then
		cd $serverPath/source && unzip $serverPath/source/${macVer}.zip
		mv ${macVer} $serverPath/lib/ffmpeg
	fi
}

Install_linux_ffmpeg()
{
	if [ ! -f $serverPath/source/ffmpeg-release-amd64-static.tar.xz ];then
		wget -O $serverPath/source/ffmpeg-release-amd64-static.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
	fi

	if [ ! -d $serverPath/lib/ffmpeg ];then
		cd $serverPath/source && tar -xvf $serverPath/source/ffmpeg-release-amd64-static.tar.xz
		#mkdir -p $serverPath/lib/ffmpeg
		mv ffmpeg-4.3-amd64-static $serverPath/lib/ffmpeg
	fi
}

if [ $sysName == 'Darwin' ]; then
		Install_mac_ffmpeg
	else
		Install_linux_ffmpeg
	fi


yum install -y libevent libevent-devel mysql-devel libjpeg* libpng* gd* zip unzip
if [ ! -d /www/wwwroot/vms ];then
	wget -O /tmp/main.zip https://codeload.github.com/midoks/vms/zip/main
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