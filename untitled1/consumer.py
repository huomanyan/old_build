import pika
import pymysql
import json
import re
import datetime

conn = pymysql.connect("localhost", "root", "123456", "ossean")
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = conn.cursor()
conn.autocommit(1)
now = datetime.datetime.now()

credentials = pika.PlainCredentials('ossean','pdl123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1',5672,'/',credentials))
channel = connection.channel()
channel.exchange_declare(exchange='broad',exchange_type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='broad', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')
pattern = r', \\"'
num = 0

insert_repos= "insert ignore into relative_memo_to_open_source_projects_1(id,osp_id,relative_memo_id,match_weight,replies_num,view_num_crawled,memo_type,view_num_trustie,has_synchronized,created_time,match_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
select_osp= "select id,name,source from open_source_projects_copy1 "
update_memos= "update relative_memos_copy1 set history =1 where id =%s"
cursor.execute(select_osp)
osp_tuples = cursor.fetchall()

def callback(ch, method, properties, body):
	global num
	record = json.dumps(body.decode('utf-8'))
	record = record.lstrip('"{"\\')
	record = record.rstrip('}"')
	record_tuple = re.split(pattern,record)
	print(len(record_tuple))
	print(record_tuple[0])
	print(record_tuple[7])
	title = "".join(record_tuple[1])
	title = title[7:-2]
	titles = str.lower(title)
	print(titles)
	title_tuple = titles.split()
	content = "".join(record_tuple[2])
	content = content[7:-2]
	contents = str.lower(content)
	content_tuple = re.split("\\\\\\\\n|\\\\\\\\r| ", contents)
	tag = "".join(record_tuple[5])
	tag = tag[7:-2]
	tags = str.lower(tag)
	print(tags)
	tags_tuple = tags.split(",")
	memo_id = "".join(record_tuple[0])
	memo_id = memo_id[5:]
	reply_num = "".join(record_tuple[7])
	reply_num = reply_num[5:]
	view_num = "".join(record_tuple[6])
	view_num = view_num[5:]
	memo_type = "".join(record_tuple[4])
	memo_type = memo_type[7:-2]
	trustie_num = "".join(record_tuple[8])
	trustie_num = trustie_num[5:]
	created_time = "".join(record_tuple[3])
	created_time = created_time[7:-2]
	print(memo_id)

	for osp_tuple in osp_tuples:
		i = "".join(osp_tuple[1])
		i = str.lower(i)
		source = "".join(osp_tuple[2])
		if source == "github":
			i_tuple = i.split("/")
			i = i_tuple[1]
		weight = 0
		if i in title_tuple:
			weight = weight + 1
		if i in content_tuple:
			weight = weight + 1
		ii = "".join(i)
		ii = "<" + ii + ">"
		if ii in tags_tuple:
			weight = weight + 1.5

		if weight > 1.5:
			# print(weight)
			num = num + 1
			cursor.execute(insert_repos, (num, osp_tuple[0], memo_id, weight, reply_num, view_num, memo_type,trustie_num, 1, created_time, now))
			cursor.execute(update_memos, (memo_id))

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()