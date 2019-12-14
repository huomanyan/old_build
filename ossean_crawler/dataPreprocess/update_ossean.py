import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='NUDTpdl@', db='ossean_production',
					   charset='utf8mb4')

cur = conn.cursor()
# select_sql= "select id from open_source_projects where id > 800000 and id < 78000000"
drop_table_sql = "drop table relative_memo_to_open_source_projects_%s"
create_table_sql = "CREATE TABLE `relative_memo_to_open_source_projects_%s` (`id` int(11) NOT NULL AUTO_INCREMENT,"+\
  "`osp_id` int(11) NOT NULL,"+\
  "`relative_memo_id` int(11) NOT NULL,"+\
  "`match_weight` float DEFAULT '0',"+\
  "`replies_num` int(11) DEFAULT NULL,"+\
  "`view_num_crawled` int(11) DEFAULT NULL,"+\
  "`memo_type` varchar(255) DEFAULT NULL,"+\
  "`view_num_trustie` int(11) DEFAULT NULL,"+\
  "`has_synchronized` tinyint(1) DEFAULT '0',"+\
  "`created_time` datetime DEFAULT NULL,"+\
  "`match_time` datetime DEFAULT NULL,"+\
  "PRIMARY KEY (`id`),"+\
  "UNIQUE KEY `osp_id_relative_memo_id_unique_index` (`osp_id`,`relative_memo_id`) USING BTREE,"+\
  "KEY `relative_memo_id_index_%s` (`relative_memo_id`) USING BTREE,"+\
  "KEY `has_synchronized_index_%s` (`has_synchronized`) USING BTREE"+\
") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"


def createTable():
	for i in range(1,21):
		table_index = i+70
		cur.execute(create_table_sql% (table_index,table_index,table_index))
	conn.commit()

def dropTable():
	for i in range(1,21):
		table_index = i+70
		cur.execute(drop_table_sql% table_index)
	conn.commit()

def deleteTableData():
    delete_sql = "delete from relative_memo_to_open_source_projects_70 where osp_id > 800000 and osp_id<78000000"
    cur.execute(delete_sql)
    conn.commit()

def split70():
	select_sql = "select distinct osp_id from relative_memo_to_open_source_projects_70 where osp_id > 800000 and osp_id<78000000"
	insert_sql = "insert into relative_memo_to_open_source_projects_%d select * from relative_memo_to_open_source_projects_70 where osp_id = %d"
	cur.execute(select_sql)
	fetchall = cur.fetchall()
	count = 0
	for prj in fetchall:
		osp_id = int(prj[0])
		table_index = 71 + (osp_id%20)
		print insert_sql % (table_index,osp_id)
		cur.execute(insert_sql % (table_index,osp_id))
		count+=1
		if count % 500==0:
			print "handle %d projects" % count
			conn.commit()
	conn.commit()
	print "success"

def getTargetTable(osp):
	base_table_name = "relative_memo_to_open_source_projects_"
	if (osp >= 770000 and osp <= 800000) or osp>78000000:
		target_table_name = base_table_name+str(70)
	elif osp > 800000 and osp < 78000000:
		tmp = 71 + osp % 20
		target_table_name = base_table_name+str(tmp)
	else:
		tmp = 1 + osp / 11000
		target_table_name = base_table_name + str(tmp)
	return target_table_name


def updateOspMemosNum(offset,batchsize):
	#1.遍历osp总表
	#2.得到匹配表并查询
	select_sql = "select id from open_source_projects limit %d,%d"
	select_count_sql = "select count(*) from %s where osp_id = %d"
	update_sql = "update open_source_projects set relative_memos_num = %d where id = %d"
	values = []

	cur = conn.cursor()
	cur.execute(select_sql % (offset,batchsize))
	osp_tuples = cur.fetchall()

	for osp in osp_tuples:
		osp_id = osp[0]
		target_table = getTargetTable(osp_id)
		cur.execute(select_count_sql % (target_table,osp_id))
		fetchall = cur.fetchall()
		if fetchall==None:
			continue

		relative_memos_count = fetchall[0]
		value = (relative_memos_count,osp_id)
		values.append(value)
		if len(values) % 500 ==0:
			cur.executemany(update_sql,values)
			conn.commit()
			del values[:]
	cur.executemany(update_sql, values)
	conn.commit()
	cur.close()






if __name__ == "__main__":
	#updateOspMemosNum()
	cur.close()
	conn.close()

	# createTable()
	# split70()











