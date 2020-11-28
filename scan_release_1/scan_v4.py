#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import datetime
import os
import ipcalc
from socket import*
import coloredlogs, logging
import sys
import configparser
import time
from hacking import*

start_time = datetime.datetime.now()

#Функция проверки существования файла
def OnFile(FileName):
	if os.path.exists(FileName):
		return True
	else:
		return False

# для раскрытия диапазонов с  / или - 
def ipRange(ip1):							

	# если есть диапазон
    ip=ip1.split('.') # ip - массив из 4х байтов
    temp=[]
    temp1=[] # для диапазонов
    temp2=[]
    for i in range(4): # идём по байтам
        if '-' in ip[i]: # если в данном байте есть
            temp=ip[i].split('-') # делим этот байт на 2 числа из диапазона
            temp1.append(temp[0]) # записываем нижние границы в массив
            temp2.append(temp[1]) # верхние - в массив
        else:
            temp1.append(ip[i]) # иначе в обе границы пишем значение байта
            temp2.append(ip[i])

  # преобразуем в инты
    for i in range(len(temp1)):
        temp1[i]= int(temp1[i])
    for i in range(len(temp2)):
        temp2[i]= int(temp2[i])

    temp=['','','',''] # каждый ip
    for i in range(temp1[0], temp2[0]+1): # перебираем каждый байт (4 цикла) от нижней границы до верхней и получившиейся ip на каждом шаге записываем в ipList
        temp[0]=i

        for j in range(temp1[1], temp2[1]+1):
            temp[1]=j

            for m in range(temp1[2], temp2[2]+1):
                temp[2]=m

                for n in range(temp1[3], temp2[3]+1):
                    temp[3]=n
                    ip=str(temp)[1:-1]
                    ip=ip.replace(", ", ".")

                    ipAdd(ip)

# для записи ip (в т.ч. с диапазонами) в ip_all.txt
def ipAdd(ip): 	
    with open("ip_all.txt", 'a+') as outfile:
        outfile.write("".join(str(ip))); outfile.write("\n")

# сам скан портов
def scan_port(ip,port):                     
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip,port))
            if result == 0:
                logging.warning('Port {} of ip {} is open' .format(port,ip))
                sock.close()
                return 1
            else:
                print('{} - {} - close' .format(port,ip))
                sock.close()
        except KeyboardInterrupt:
            logging.critical("You pressed Ctrl+C")
            sys.exit()
        except gaierror:
            logging.critical('Hostname could not be resolved. Exiting')
            sys.exit()
        except error:
            print("Couldn't connect to server")
            sys.exit()
        	
def Main(fff):
    parse = argparse.ArgumentParser(description='Scanner')   # Создаем парсер
    # parse.add_argument('-i', action='store', dest='ip', help='File path with ip, example: \'ip.txt\'')  # Добавляем опцию, путь к файлу с ip
    parse.add_argument('-l', action='store', dest='logins', help='File path with logins, example: \'logins.txt\'')  # Добавляем опцию, путь к файлу с логинами
    parse.add_argument('-p', action='store', dest='passwords', help='File path with passwords, example: \'password.txt\'')  # Добавляем опцию, путь к файлу с паролями
    args = parse.parse_args()      # Получаем аргументы
    if (args.logins == None) or (args.passwords == None):      # @@(args.ip == None) or @@  Если аргументов нет то
        print (parse.print_help())  # Выводим хэлп
        exit()     # Выход
    else:   # Иначе, если аргументы есть то
        #Проверка на существование файлов
    #     if (OnFile(args.ip) != True):
    #         print ("\x1b[31m" +str(datetime.datetime.now()) + " - ip List file no found\x1b[0m")
    #         exit()
        if (OnFile(args.logins) != True):
            print ("\x1b[31m" +str(datetime.datetime.now()) + " - logins List file no found\x1b[0m")
            exit()
        if (OnFile(args.passwords) != True):
            print ("\x1b[31m" +str(datetime.datetime.now()) + " - passwords List file no found\x1b[0m")
            exit()

    # iip = args.ip 
    llog = args.logins
    ppas = args.passwords




    # очистка промежуточных файлов перед сканированием
    open("ip_all.txt","w").close()
    open("csv.txt","w").close() 

    # для записи ip (в т.ч. с диапазонами) в ip_all.txt 
    strings = fff.read().splitlines()
    for i in range(len(strings)):   # Добавление ip
        if ('-' in strings[i]):     #ip из диапазонов
            ipRange(strings[i])
        elif ('/' in strings[i]):   #ip с маской
            for x in ipcalc.Network(strings[i]):
                ipAdd(str(x))
        else: # простой ip						 
            ipAdd(strings[i])						 

    # для красивого вывода
    coloredlogs.install() 
    print("-" * 40)
    print("\033[34m Please wait, scanning in progress...\033[0m")
    print("-" * 40)

    # настройка программы из файла setting.conf
    conf = configparser.RawConfigParser()
    conf.read("setting.conf")
    time_sleep = conf.getfloat("time_sleep", "time")
    g_db = conf.get("geoip_db", "name")
    log_clear = conf.get("log.txt", "clear")

    mysql_port = conf.getint("default_ports", "MySQL")
    postresql_port = conf.getint("default_ports", "PostgreSQL")
    mongodb_port = conf.getint("default_ports", "MongoDB")
    elasticsearch_port = conf.getint("default_ports", "Elasticsearch")

    range_ports = [mysql_port,postresql_port,mongodb_port,elasticsearch_port]

    if log_clear == 'on':
        open("log.txt","w").close()

    # скан портов и запись в csv.txt в формате: ip:port1,port2
    with open("ip_all.txt", 'r') as f:                     
        strings = f.read().splitlines()
        for i in range(len(strings)):
            str1 = strings[i]+":"
            print(str1)
            for port in range_ports: 
                if (scan_port(strings[i],port)==1):
                    str1 += str(port)+","
            if str1 != (strings[i]+":"):
                str1=str1[0:-1]
                with open("csv.txt", 'a+') as csvfile:
                    csvfile.write("".join(str(str1))); csvfile.write("\n")
                print("+" * 90)
            time.sleep(time_sleep)

    # для красивого вывода
    print("-" * 40)
    print("\033[34m \t Scan completed \033[0m")
    print("-" * 40)

    # из файла csv.txt берутся ip и порты и производится подключение к БД с записью результатов в log.txt
    with open("csv.txt", "r") as csv_file:
        str1 = csv_file.read().splitlines()
        for line in str1:
            str2=(str(line)).split(":")
            ports=(str(str2[1])).split(",")

            ip = str2[0]
            logging.info(ip)
            
            # запись в Log.txt информации об ip 
            with open("log.txt", 'a+') as outfile:
                logALL(ip,g_db)
           
            with open(llog) as f1:
                content = f1.read()
                logins_list = content.split('\n')
            
                with open(ppas) as f2:
                    content = f2.read()
                    password_list = content.split('\n')

                    for i in range(len(ports)):
                        port = int(ports[i])
                        print("port:"+str(port)+"--")
                        with open("log.txt", 'a+') as outfile:
                            outfile.write("\nopen_port: ");  outfile.write("".join(str(port)))
                            if port == mysql_port:
                                # with open("log.txt", 'a+') as outfile:
                                outfile.write(" --- MySQL\n")
                                Main_1(ip,port,logins_list,password_list)

                            if port == postresql_port:
                                # with open("log.txt", 'a+') as outfile:
                                outfile.write(" --- PostgreSQL\n")
                                Main_2(ip,port,logins_list,password_list)

                            if port == mongodb_port:
                                # with open("log.txt", 'a+') as outfile:
                                outfile.write(" --- MongoDB\n")
                                Main_3(ip,port,logins_list,password_list)

                            if port == elasticsearch_port:
                                # with open("log.txt", 'a+') as outfile:
                                outfile.write(" --- Elasticsearch\n")
                                Main_4(ip,port,logins_list,password_list)
                                
                    print("+" * 90)
    print(datetime.datetime.now() - start_time)
    print("\033[34m Scanning completed...\033[0m")

# if __name__=="__main__":
# 	Main()