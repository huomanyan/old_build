#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-03-18 16:38:40
# @Author  : Letitia Chou (lititia96@outlook.com)
# @Link    : https://blog.csdn.net/Letitia96
# @Version : $Id$

import pika
from mysqlconn import MyPymysqlPool
import pymysql
import json
from datetime import *
from threading import Timer

def parser(channel, conf_db='dbMysql2', table='ossean.relative_memos_copy1', num=20, history_flag=1):
	mysql = MyPymysqlPool(conf_db)

	query_sql = "select * from " + table + " where history is null order by id desc limit " + str(num)
	results = mysql.getAll(query_sql)

	if results is None:
		timer = Timer(10, parser)
		timer.start()
		return

	for result in results:
		record = {}
		record['title'] = result[1]
		record['content'] = result[2]
		record['created_time'] = str(result[3])
		record['updated_time'] = str(result[4])
		record['memos_type'] = result[5]
		record['tags'] = result[6]
		record['source'] = result[7]
		record['url'] = result[8]
		record['url_md5'] = result[9]
		record['author_url'] = result[10]
		record['author_url'] = result[11]
		record['view_num'] = result[12]
		record['review_num'] = result[13]
		record['view_num_ossean'] = result[12]
		record['extracted_time'] = str(result[15])
		record['history'] = result[16]
		
		record_json = json.dumps(record)
		message = record_json.encode('utf-8')
		channel.basic_publish(exchange='broad', routing_key='', body=message)



if __name__ == '__main__':
	credentials = pika.PlainCredentials('ossean','pdl123456')
	connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1',5672,'/',credentials))
	chan = connection.channel()

	chan.exchange_declare(exchange='broad',exchange_type='fanout')
	parser(channel=chan)

	connection.close()