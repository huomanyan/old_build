#encoding:utf-8
import pymysql
conn =  pymysql.connect(host='10.107.10.110', port=3306, user='root', passwd='111111', db='ghtorrent_2017_5',
                       charset='utf8mb4')
num_none = 0
print(conn)

#1.现根据url查找repo_id
#2.根据id查找一年内每三个月的contri
#3.根据contri计算

time_list = ['2016-5','2016-8','2016-11','2017-02','2017-05']

def getRepoUrlList(offset,batchsize):
    cur = conn.cursor()
    select_sql = "select id,url from osp_github_match_filter_gh limit %d,%d"
    cur.execute(select_sql % (offset,batchsize)) #
    prj_tuples = cur.fetchall()
    print("repo length : %d" % len(prj_tuples))
    cur.close()
    return prj_tuples

def getRepoUrlList_tmp():
    cur = conn.cursor()
    select_sql = "select id,url from osp_github_match_filter_gh where id in (select id from ossean_commits_incre where id not in (select id from ossean_contri))"
    cur.execute(select_sql) #
    prj_tuples = cur.fetchall()
    print("repo length : %d" % len(prj_tuples))
    cur.close()
    return prj_tuples


def MineContributors(offset,batchsize):
    cur = conn.cursor()
    select_sql = "select id from projects where url = '%s'"
    insert_sql = "insert into ossean_contri(id, s1, s2, s3, s4, union12, diff21,union23, diff32,union34, diff43) values(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)"

    src_repo_list = getRepoUrlList_tmp()#getRepoUrlList(offset,batchsize)

    repo_count = 0
    for prj in src_repo_list:
        cur.execute(select_sql % prj[1])
        fetchone = cur.fetchone()
        if fetchone ==None:
            continue
        repo_id = fetchone[0]

        sql = "select DISTINCT committer_id from commits where project_id=%d and created_at<= '%s-01 00:00:00' and created_at > '%s-01 00:00:00' "

        season_dict = dict()
        for time_index in range(len(time_list)-1):
            cur.execute(sql % (repo_id,time_list[time_index+1],time_list[time_index]))
            committer_id_tuples = cur.fetchall()
            if len(committer_id_tuples)==0:
                print("no committer info %d" %repo_id)
                season_dict[time_index+1] = None
                continue
            tmp = set()
            for commiter_id in committer_id_tuples:
                tmp.add(commiter_id[0])
            if None in tmp:
                tmp.remove(None)
            season_dict[time_index + 1] = tmp

        people_list = list()
        for i in [1, 2, 3, 4]:
            cur_count = 0 if season_dict[i]==None else len(season_dict[i])
            people_list.append(cur_count)
        for i in [1,2,3]:
            if(season_dict[i]==None or season_dict[i+1] ==None):
                cross_count = 0
                incre_count = 0
            else:
                cross_count = len(season_dict[i] & season_dict[i+1])
                incre_count = len(season_dict[i+1] - season_dict[i])
            people_list.append(cross_count)
            people_list.append(incre_count)

        value = (prj[0],people_list[0],people_list[1],people_list[2],people_list[3],people_list[4],people_list[5],people_list[6],people_list[7],people_list[8],people_list[9])
        cur.execute(insert_sql % value)

        repo_count += 1
        if repo_count % 50 == 0:
            conn.commit()
            print("handled %d project" % repo_count)
    print("handled %d project" % repo_count)
    print("non commits have : %d projects" % num_none)
    conn.commit()
    cur.close()

import sys
if __name__ == '__main__':
    MineContributors(int(sys.argv[1]),int(sys.argv[2]))
    conn.close()
