#encoding:utf-8
import pymysql
from datetime import datetime
conn = pymysql.connect(host='10.107.10.110', port=3306, user='root', passwd='111111', db='ghtorrent_2017_5',
                       charset='utf8mb4')
print(conn)

#1.现根据url查找repo_id
#2.根据id查找一年内每三个月的issue的平均修复时间，用issues & issues表


time_list = ['2016-11','2017-02','2017-05']

def getRepoUrlList(offset,batchsize):
    cur = conn.cursor()
    select_sql = "select id,url from osp_github_match_filter_gh where ingh_flag = 0 limit %d,%d"
    cur.execute(select_sql % (offset,batchsize))
    prj_tuples = cur.fetchall()
    print("repo length : %d" % len(prj_tuples))
    cur.close()
    return prj_tuples

def getIssueCountSea(offset,batchsize):
    cur = conn.cursor()
    select_repo_sql = "select id from projects where url = '%s'"
    select_issue_count_sql = "SELECT count(*) from github_api where pull_request= 0 and repo_id =%d and created_at >= '2017-02-01 00:00:00'"
    insert_sql = "update ossean_issues_repair set incre_sea = %d where id = %d"
    src_repo_list = getRepoUrlList(offset,batchsize)

    repo_count = 0
    for prj in src_repo_list:
        cur.execute(select_repo_sql % prj[1])
        fetchone = cur.fetchone()
        if fetchone ==None:
            continue
        repo_id = fetchone[0]
        cur.execute(select_issue_count_sql % repo_id)
        fetchone = cur.fetchone()
        if fetchone == None:
            issue_incre_count = 0
        else:
            issue_incre_count = fetchone[0]
        cur.execute(insert_sql % (issue_incre_count,prj[0]))
        repo_count += 1
        if repo_count % 100 == 0:
            conn.commit()
    print "success"
    conn.commit()
    cur.close()



def IssuesRepair(offset,batchsize):
    cur = conn.cursor()
    select_repo_sql = "select id from projects where url = '%s'"

    select_issue_sql = "select id,created_at from github_api where repo_id = %d and created_at<= '%s-01 00:00:00' and created_at > '%s-01 00:00:00' "
    close_select_sql = "select created_at from issue_events  where issue_id=%d and action='closed';"

    insert_sql = "insert into ossean_issues_repair(id, s3_issue_count, s3_issue_time, s4_issue_count, s4_issue_time) VALUES (%d,%d,%d,%d,%d)"
    src_repo_list = getRepoUrlList(offset,batchsize)

    repo_count = 0
    starttime = datetime.now()
    for prj in src_repo_list:
        cur.execute(select_repo_sql % prj[1])
        fetchone = cur.fetchone()
        if fetchone ==None:
            continue
        repo_id = fetchone[0]

        season_dict = dict()
        for time_index in range(2):
            cur.execute(select_issue_sql % (repo_id,time_list[time_index+1],time_list[time_index]))
            issues_tuples = cur.fetchall()
            issue_count = 0
            total_time_diff = 0
            for issue in issues_tuples:
                created_time = issue[1]
                cur.execute(close_select_sql % issue[0])
                fetchone = cur.fetchone()
                if fetchone is None:
                    continue

                closed_time = fetchone[0]
                issue_count += 1
                #计算时间差值,并累加
                time_diff = (closed_time-created_time).seconds /60
                total_time_diff += time_diff
            season_dict[time_index+1] = (issue_count,total_time_diff)


        value = (prj[0],season_dict[1][0],season_dict[1][1],season_dict[2][0],season_dict[2][1])
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
    # IssuesRepair(int(sys.argv[1]),int(sys.argv[2]))
    getIssueCountSea(int(sys.argv[1]),int(sys.argv[2]))
    conn.close()
