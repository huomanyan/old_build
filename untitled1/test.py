# -*- coding: utf-8 -*-
import pymysql
import datetime
import time
import redis
# 打开数据库连接
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)
conn = pymysql.connect("localhost", "root", "123456", "ossean")
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = conn.cursor()
conn.autocommit(1)
now = datetime.datetime.now()

insert_repos= "insert ignore into relative_memo_to_open_source_projects_1(id,osp_id,relative_memo_id,match_weight,replies_num,view_num_crawled,memo_type,view_num_trustie,has_synchronized,created_time,match_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
select_memos= "select id,title,content,created_time,memo_type,tags,view_num,review_num,view_num_ossean from relative_memos_copy1 "
update_memos= "update relative_memos_copy1 set history =1 where id =%s"

def match():
    global num, weight, t
    r=redis_client.scard("osp_id")
    print(r)
    if r==0:
        return
    repo=redis_client.spop("osp_id")
    result = str(repo, encoding='utf-8')
    repo_id=result.split(" ",1)[0]
    name=result.split(" ",1)[1]
    t=0
    i=name
    print(i)

    cursor.execute(select_memos)
    str_tuple = cursor.fetchall()
    length = len(str_tuple)
    while (t<length):
        #print(str_tuple[t][1])
        title_tuple = str_tuple[t][1].split( )
        content_tuple = str_tuple[t][2].split( )
        tags_tuple = str_tuple[t][5].split(",")

        weight = 0
        if i in title_tuple:
            weight = weight + 1
        if i in content_tuple:
            weight = weight + 1

        ii = "<" + i + ">"
        if ii in tags_tuple:
            weight = weight + 1.5
        if weight > 0:
            # print(weight)
            num = num + 1
            cursor.execute(insert_repos, (num, repo_id, str_tuple[t][0], weight, str_tuple[t][7], str_tuple[t][6], str_tuple[t][4],str_tuple[t][8], 1, str_tuple[t][3], now))


        t+= 1

import sys
if __name__ == '__main__':
    weight = 0
    num = 0
    while(1):
        match()
        #time.sleep(30)
    conn.close()