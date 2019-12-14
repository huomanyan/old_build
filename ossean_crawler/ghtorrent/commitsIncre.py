#encoding:utf-8
import pymysql
conn =  pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='111111', db='ghtorrent_2017_5',
                       charset='utf8mb4')
print(conn)

#1.现根据url查找repo_id
#2.根据id查找一年内每三个月的commits的增量，用commits表，没考虑fork信息


time_list = ['2016-5','2016-8','2016-11','2017-02','2017-05']

def getRepoUrlList(offset,batchsize):
    cur = conn.cursor()
    select_sql = "select id,url from osp_github_match_filter_gh limit %d,%d"
    cur.execute(select_sql % (offset,batchsize)) #
    prj_tuples = cur.fetchall()
    print("repo length : %d" % len(prj_tuples))
    cur.close()
    return prj_tuples

def MineCommitsIncre(offset,batchsize):
    cur = conn.cursor()
    select_repo_sql = "select id from projects where url = '%s'"

    update_sql = "update osp_github_match_filter_gh set ingh_flag = 1 where id = %d" #在ghtorrent中没有这个id
    select_sql = "select count(*) from commits where project_id = %d and created_at<= '%s-01 00:00:00' and created_at > '%s-01 00:00:00'" ;
    insert_sql = "insert into ossean_commits_incre(id, s1, s2, s3, s4) VALUES (%d,%d,%d,%d,%d)"

    src_repo_list = getRepoUrlList(offset,batchsize)

    repo_count = 0
    for prj in src_repo_list:
        cur.execute(select_repo_sql % prj[1])
        fetchone = cur.fetchone()
        if fetchone ==None:
            cur.execute(update_sql % prj[0])
            continue
        repo_id = fetchone[0]

        season_dict = dict()
        for time_index in range(4):
            cur.execute(select_sql % (repo_id,time_list[time_index+1],time_list[time_index]))
            commits_num = cur.fetchone()[0]
            season_dict[time_index + 1] = commits_num

        value = (prj[0],season_dict[1],season_dict[2],season_dict[3],season_dict[4])
        cur.execute(insert_sql % value)

        repo_count += 1
        if repo_count % 50 == 0:
            conn.commit()
            print("handled %d project" % repo_count)
    conn.commit()
    print("handled %d project" % repo_count)
    cur.close()

import sys
if __name__ == '__main__':
    MineCommitsIncre(int(sys.argv[1]),int(sys.argv[2]))
    conn.close()
