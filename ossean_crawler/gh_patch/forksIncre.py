#encoding:utf-8
import pymysql
from datetime import datetime
conn = pymysql.connect(host='10.107.10.110', port=3306, user='root', passwd='111111', db='ghtorrent_2017_5',
                       charset='utf8mb4')
print(conn)

#1.现根据url查找repo_id
#2.根据id查找一年内每三个月的forks的增量


time_list = ['2016-5','2016-8','2016-11','2017-02','2017-05']

def getRepoUrlList(offset,batchsize):
    cur = conn.cursor()
    select_sql = "select id,url from projects_ossean limit %d,%d"
    cur.execute(select_sql % (offset,batchsize))
    prj_tuples = cur.fetchall()
    print("repo length : %d" % len(prj_tuples))
    cur.close()
    return prj_tuples

def IssuesRepair(offset,batchsize):
    cur = conn.cursor()

    select_forks_sql = "select count(*) from projects where forked_from = %d and created_at<= '%s-01 00:00:00' and created_at > '%s-01 00'"
    insert_sql = "insert into ossean_forks_incre_patch(id, s1, s2, s3, s4) VALUES (%d,%d,%d,%d,%d)"
    src_repo_list = getRepoUrlList(offset,batchsize)

    repo_count = 0
    starttime = datetime.now()
    for prj in src_repo_list:

        repo_id = prj[0]

        season_dict = dict()
        for time_index in range(4):
            cur.execute(select_forks_sql % (repo_id, time_list[time_index + 1], time_list[time_index]))
            forks_num = cur.fetchone()[0]
            season_dict[time_index + 1] = forks_num

        value = (prj[0], season_dict[1], season_dict[2], season_dict[3], season_dict[4])
        cur.execute(insert_sql % value)

        repo_count += 1
        if repo_count % 50 == 0:
            endtime = datetime.now()
            conn.commit()
            print("handle %d repositories cost %s seconds" % (repo_count, (endtime - starttime).seconds))
    conn.commit()
    endtime = datetime.now()
    print("handle %d repositories cost %s seconds" % (repo_count, (endtime - starttime).seconds))
    cur.close()


import sys
if __name__ == '__main__':
    IssuesRepair(int(sys.argv[1]),int(sys.argv[2]))
    conn.close()
