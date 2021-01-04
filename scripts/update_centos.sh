#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

# unalias cp
# alias cp='cp -i'

wget -O /tmp/main.zip https://codeload.github.com/midoks/vms/zip/main
cd /tmp && unzip /tmp/main.zip
/usr/bin/cp -rf  /tmp/vms-main/* /www/wwwroot/vms
rm -rf /tmp/main.zip
rm -rf /tmp/vms-main

cd /www/wwwroot/vms && ./cli.sh restart