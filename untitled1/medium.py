import pymysql
import datetime
import time
# 打开数据库连接
conn = pymysql.connect("localhost", "root", "123456", "ossean")
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = conn.cursor()
conn.autocommit(1)
now = datetime.datetime.now()

insert_repos= "insert ignore into relative_memo_to_open_source_projects_2(id,osp_id,relative_memo_id,match_weight,replies_num,view_num_crawled,memo_type,view_num_trustie,has_synchronized,created_time,match_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
select_memos= "select id,title,content,created_time,memo_type,tags,view_num,review_num,view_num_ossean from relative_memos_copy2 "
update_memos= "update relative_memos_copy2 set history =1 where id =%s"

select_osp= "select id,name,source from open_source_projects_copy1 "
cursor.execute(select_osp)
osp_tuples = cursor.fetchall()

def match():
    global num, weight, t
    t=0
    cursor.execute(select_memos)
    str_tuple = cursor.fetchall()
    print(str_tuple[0])
    length = len(str_tuple)
    print(length)
    while (t<length):
        #print(str_tuple[t][1])
        title = "".join(str_tuple[t][1])
        titles = str.lower(title)
        title_tuple = titles.split( )
        content = "".join(str_tuple[t][2])
        contents = str.lower(content)
        content_tuple = contents.split( )
        tag = "".join(str_tuple[t][5])
        tags = str.lower(tag)
        tags_tuple = tags.split(",")

        for osp_tuple in osp_tuples:
            i = "".join(osp_tuple[1])
            i = str.lower(i)
            source = "".join(osp_tuple[2])
            if source == "github":
                i_tuple= i.split("/")
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
                #print(weight)
                num = num + 1
                cursor.execute(insert_repos, (num,osp_tuple[0],str_tuple[t][0],weight,str_tuple[t][7],str_tuple[t][6],str_tuple[t][4],str_tuple[t][8],1,str_tuple[t][3],now))
                #cursor.execute(update_memos,(str_tuple[t][0]))
        t+= 1

import sys
if __name__ == '__main__':
    weight = 0
    num = 0
    while(1):
        time.sleep(5)
        match()
    conn.close()