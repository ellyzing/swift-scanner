#!/bin/sh

apt install python3.8 -y
apt install python3-pip -y
apt install libgeoip-dev -y
apt-get upgrade python3 -y
pip3 install --upgrade pip3
pip3 install argparse six datetime coloredlogs configparser geoip2 python-geoip-geolite2 pymysql pymongo elasticsearch psycopg2
pip3 install ipcalc 
