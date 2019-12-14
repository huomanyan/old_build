# encoding : utf-8
import pymysql
conn = pymysql.connect(host='10.107.10.110', port=3306, user='root', passwd='111111', db='ghtorrent_2017_5',
                       charset='utf8mb4')
conn_local = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ghtorrent_2017_5', charset='utf8mb4')


def getPrjList():
    cur = conn.cursor()
    select_sql = 'select id from projects_400_id'
    cur.execute(select_sql)
    prj_tuples = cur.fetchall()
    prj_list = []
    for prj in prj_tuples:
        prj_list.append(int(prj[0]))
    print("prj length : %d" % len(prj_list))
    cur.close()
    return prj_list

time_list = ['2016-10','2016-11','2016-12','2017-01','2017-02','2017-03','2017-04']
def getPrjIssueRepoter(i):
    #804
    prj_list = getPrjList()
    #issue
    select_issue_sql_1 = "select distinct reporter_id from github_api where repo_id = %d and created_at<= '%s-01 00:00:00'"
    select_issue_sql_2 = "select distinct reporter_id from github_api where repo_id = %d and created_at<= '%s-01 00:00:00' and created_at> '%s-01 00:00:00'"
    insert_sql = "insert into project_issue_reporter(repo_id, user_id,time) VALUES (%s,%s,'%s')"
    cur = conn.cursor()
    handled_count = 0
    for prj in prj_list:
        if i==0:
            cur.execute(select_issue_sql_1 % (prj, time_list[i]))
        else:
            cur.execute(select_issue_sql_2 % (prj, time_list[i],time_list[i-1]))

        reporter_tuples = cur.fetchall()
        for reporter in reporter_tuples:
            if reporter[0] is not None:
                value = (int(prj), int(reporter[0]),pymysql.escape_string(time_list[i]+"-01 00:00:00"))
                cur.execute(insert_sql % value)

        handled_count += 1
        if handled_count % 50 == 0:
            conn.commit()
            print("handled %d projects" % handled_count)
    conn.commit()
    print("handled %d projects" % handled_count)
    cur.close()


def insertIssueRepoterCross(time_index):
    prj_list = getPrjList()
    if time_index==0:
        insert_sql = 'insert into project_issuerepoter_cross_total_time (crossNum_%s,projectA,projectB) values (%s,%s,%s)'
    else:
        insert_sql = 'update project_issuerepoter_cross_total_time set crossNum_%s = %d where projectA = %d and projectB = %d'
    issue_sql = "select DISTINCT user_id from project_issue_reporter where repo_id = %d and time <= '%s-01 00:00:00'"
    store = dict()

    cur = conn.cursor()
    for i in prj_list:
        cur.execute(issue_sql % (i,time_list[time_index]))
        repoter_tuples = cur.fetchall()
        contributors_set = set() #存储issue reporter
        for j in repoter_tuples:
            contributors_set.add(j[0])
        store[i] = contributors_set

    count = 0
    for i in range(len(prj_list)):
        for j in prj_list[i+1:]: # 不重复计算
            count+=1
            cross_count = store[prj_list[i]] & store[j]
            value = (time_list[time_index].replace('-','_'),len(cross_count),prj_list[i],j)
            cur.execute(insert_sql % value)
            if count % 500 == 0:
                conn.commit()
                print("handled %d entrys" % count)
    conn.commit()
    cur.close()

def calDistribution():
    insert_sql = 'insert into issue_repo_distribution (repo_id,reporter_id,issue_count) select repo_id,reporter_id,count(issue_number) from github_api where repo_id = %d GROUP BY reporter_id;'
    cur = conn_local.cursor()
    prjList = getPrjList()
    for prj in prjList:
        cur.execute(insert_sql % prj)
    conn_local.commit()
    cur.close()

#计算方差
from sklearn import preprocessing
import numpy as np

def countVariance(prjlist):
    select_sql = 'select issue_count from issue_repo_distribution where repo_id = %d'
    update_sql = 'update projects_400_id set issue_variance=%f  where id = %d'
    # select_count_sql = 'select count(issue_number) from github_api where repo_id = %d'
    # select_reporter_sql = 'select count(distinct reporter_id) from github_api where repo_id = %d'

    cur = conn_local.cursor()
    cur_110 = conn.cursor()
    # cur.execute(select_count_sql % prj)
    # prj_issue_count = cur.fetchone()[0]
    # cur.execute(select_reporter_sql % prj)
    # prj_reporter_count = cur.fetchone()[0]
    # avg = float(prj_issue_count) / prj_reporter_count
    for prj in prjlist:
        cur.execute(select_sql % prj)
        fetchall = cur.fetchall()
        list = []
        for i in fetchall:
            list.append(i[0])

        X = np.array(list)
        min_max_scaler = preprocessing.MinMaxScaler()
        X_minMax = min_max_scaler.fit_transform(X)
        X_avg= np.mean(X_minMax)
        variance = 0.0

        for i in X_minMax:
            variance += (i-X_avg)**2

        print(variance/len(list))
        cur_110.execute(update_sql % (variance/len(list),prj))
        conn.commit()
    cur.close()
    cur_110.close()


if __name__ == '__main__':
    # for i in range(2,7):
    #     insertIssueRepoterCross(i)
    # getPrjIssueRepoter(6)
    # calDistribution()
    countVariance([3213843,7709533])
    conn.close()
    conn_local.close()
