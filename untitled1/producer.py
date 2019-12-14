import pika
from mysqlconn import MyPymysqlPool
#import time
import json
from datetime import *
#from threading import Timer

def parser( conf_db='dbMysql2', table='ossean.relative_memos_copy2', num=858):
	mysql = MyPymysqlPool(conf_db)

	query_sql = "select id,title,content,created_time,memo_type,tags,view_num,review_num,view_num_ossean from " + table + " order by id desc limit 20 "
	results = mysql.getAll(query_sql)
	print(results)

	#if results is None:
		#timer = Timer(10, parser)
		#timer.start()
		#return

	for result in results:
		record = {}
		record[0] = result[0]
		record[1] = result[1]
		record[2] = result[2]
		record[3] = str(result[3])
		record[4] = result[4]
		record[5] = result[5]
		record[6] = result[6]
		record[7] = result[7]
		record[8] = result[8]

		record_json = json.dumps(record)
		message = record_json.encode('utf-8')
		chen = connection.channel()

		chen.exchange_declare(exchange='broad', exchange_type='fanout')
		channel=chen
		channel.basic_publish(exchange='broad', routing_key='', body=message)


import time
if __name__ == '__main__':
	credentials = pika.PlainCredentials('ossean','pdl123456')
	connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1',5672,'/',credentials))
	#chen = connection.channel()

	#chen.exchange_declare(exchange='broad',exchange_type='fanout')
	while(1):
		parser()
		time.sleep(60)


	connection.close()