#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-03-18 22:49:43
# @Author  : Letitia Chou (lititia96@outlook.com)
# @Link    : https://blog.csdn.net/Letitia96
# @Version : $Id$

import pika
import json
import re

credentials = pika.PlainCredentials('ossean','pdl123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1',5672,'/',credentials))
channel = connection.channel()

channel.exchange_declare(exchange='broad',exchange_type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='broad', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')
pattern = r', \\"'

def callback(ch, method, properties, body):
	record = json.dumps(body.decode('utf-8'))
	record = record.lstrip('"{"\\')
	record = record.rstrip('}"')
	record_tuple = re.split(pattern, record)
	content = "".join(record_tuple[2])
	content = content[7:-2]
	contents = str.lower(content)
	content_tuple = re.split("\\\\\\\\n|\\\\\\\\r| ",contents)
	#print()
	if len(record_tuple)==9:
		for i in content_tuple:
			print(i)


channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()