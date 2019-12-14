import pymysql
import datetime
import time
# 打开数据库连接
conn = pymysql.connect("localhost", "root", "123456", "ossean")
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = conn.cursor()
conn.autocommit(1)
now = datetime.datetime.now()

insert_repos= "insert ignore into relative_memo_to_open_source_projects_1(id,osp_id,relative_memo_id,match_weight,replies_num,view_num_crawled,memo_type,view_num_trustie,has_synchronized,created_time,match_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
select_memos= "select id,title,content,created_time,memo_type,tags,view_num,review_num,view_num_ossean from relative_memos_copy1 where history=0"
update_memos= "update relative_memos_copy1 set history =1 where id =%s"

select_osp= "select id,name from open_source_projects_copy1 "
cursor.execute(select_osp)
osp_tuples = cursor.fetchall()

def match():
    global num, weight, t
    t=0
    cursor.execute(select_memos)
    str_tuple = cursor.fetchall()
    length = len(str_tuple)
    print(length)
    while (t<length):
        #print(str_tuple[t][1])
        title_tuple = str_tuple[t][1].split( )
        content_tuple = str_tuple[t][2].split( )
        tags_tuple = str_tuple[t][5].split(",")

        for osp_tuple in osp_tuples:
            i = "".join(osp_tuple[1])
            weight = 0
            for j in title_tuple:
                # print(j)
                if i == j:
                    weight = weight + 1
                    break
            for k in content_tuple:
                if i == k:
                    weight = weight + 1
                    break
            for l in tags_tuple:
                ii = "".join(i)
                ii = "<" + ii + ">"

                if ii == l:
                    weight = weight + 1.5
                    break
            if weight > 0:
                #print(weight)
                num = num + 1
                cursor.execute(insert_repos, (num,osp_tuple[0],str_tuple[t][0],weight,str_tuple[t][7],str_tuple[t][6],str_tuple[t][4],str_tuple[t][8],1,str_tuple[t][3],now))
                cursor.execute(update_memos,(str_tuple[t][0]))
        t+= 1
        print(t)
import sys
if __name__ == '__main__':
    weight = 0
    num = 0
    while(1):
        time.sleep(5)
        match()
    conn.close()