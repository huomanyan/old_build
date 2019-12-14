import pymysql
conn = pymysql.connect(host='10.107.10.110', port=3306, user='root', passwd='111111', db='ghtorrent_2017_5',
                       charset='utf8mb4')
conn_local = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ghtorrent_2017_5', charset='utf8mb4')

#test set 516
def getTestPrjList():
    cur = conn_local.cursor()
    select_sql = 'select id from projects_400_id where num_time_test >= 50'
    cur.execute(select_sql)
    prj_tuples = cur.fetchall()
    prj_list = []
    for prj in prj_tuples:
        prj_list.append(int(prj[0]))
    print("test prj length : %d" % len(prj_list))
    cur.close()
    return prj_list

#train set 682
def getTrainPrjList():
    cur = conn_local.cursor()
    select_sql = 'select id from projects_400_id where num_time_train >= 400 and bug_ratio>=0.2 and bug_ratio<=0.8 or num_time_test>=50'
    cur.execute(select_sql)
    prj_tuples = cur.fetchall()
    prj_list = []
    for prj in prj_tuples:
        prj_list.append(int(prj[0]))
    print("train prj length : %d" % len(prj_list))
    cur.close()
    conn_local.close()
    return prj_list

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

def getPrjMainDever():
    #842
    prj_list = getPrjList()
    #pull request
    select_pr_sql = 'select id from pull_requests where base_repo_id = %d'
    pr_select_sql = "select actor_id from pull_request_history where pull_request_id=%d and action in ('merged','reopened','closed')"
    #issue
    select_issue_sql = "select id,reporter_id from github_api where repo_id = %d "
    reopen_select_sql = "select actor_id from issue_events  where issue_id=%d and action='reopened'"
    close_select_sql = "select actor_id from issue_events  where issue_id=%d and action='closed'"

    cur = conn.cursor()
    member_list = set()
    handled_count = 0
    values = []
    for prj in prj_list:
        cur.execute(select_pr_sql % prj)
        pr_tuples = cur.fetchall()
        #pr
        for pr in pr_tuples:
            cur.execute(pr_select_sql % (pr[0]))
            fetch_tmp = cur.fetchall()

            for i in fetch_tmp:
                member_list.add(i[0])
        #issue
        cur.execute(select_issue_sql % (prj))
        issue_tuples = cur.fetchall()
        for issue in issue_tuples:
            cur.execute(reopen_select_sql % issue[0])
            reopen_tmp = cur.fetchall()
            for j in reopen_tmp:#reopen
                member_list.add(j[0])
            cur.execute(close_select_sql % issue[0])
            close_tmp = cur.fetchall()
            for i in close_tmp:#open & close is not same person
                if issue[1] is not None and issue[1] != i[0]:
                    member_list.add(i[0])
        if None in member_list:
            member_list.remove(None)
        for mem in member_list:
            value = (int(prj), int(mem))
            values.append(value)
        member_list.clear()
        handled_count += 1
        if handled_count % 50 == 0:
            cur.executemany("insert into project_maindev_2017_5(repo_id,user_id) values(%s,%s)", values)
            conn.commit()
            print("handled %d projects" % handled_count)
            values.clear()
    if len(values) > 0:
        cur.executemany("insert into project_maindev_2017_5(repo_id,user_id) values(%s,%s)", values)
        conn.commit()
    print("handled %d projects" % handled_count)
    cur.close()


def insertMainDevCross(prj_list,currenttime):#currenttime 2016_10

    getcontri_table = "project_maindev_" + currenttime
    insertcontri_table = "project_maindev_cross_" + currenttime #project_maindev_cross_2017_5

    insert_sql = 'insert into '+insertcontri_table+' (projectA,projectB,crossNum) values (%s,%s,%s)'
    maindev_sql = 'select user_id from '+getcontri_table+' where repo_id = %d'
    store = dict()

    cur = conn.cursor()
    for i in prj_list:
        cur.execute(maindev_sql % i)
        contributors_tuples = cur.fetchall()
        contributors_set = set() #存储项目的贡献人员
        for j in contributors_tuples:
            contributors_set.add(j[0])
        store[i] = contributors_set

    values = []
    count = 0
    for i in range(len(prj_list)):
        count += 1
        for j in prj_list[i+1:]: # 不重复计算
            cross_count = store[prj_list[i]] & store[j]
            value = (prj_list[i],j,len(cross_count))
            values.append(value)
            if len(values) > 5000:
                cur.executemany(insert_sql, values)
                conn.commit()
                print("handled %d project" % count)
                print("insert into db: %d entrys" % len(values))
                del values[:]
    if len(values) > 0:
        cur.executemany(insert_sql, values)
    conn.commit()
    cur.close()

if __name__ == '__main__':
    # 682
    # prj_list = getTrainPrjList()
    # time_list = ['2016_10','2016_11','2016_12','2017_1','2017_2','2017_3','2017_4']
    # for time_ in time_list:
    #     insertMainDevCross(prj_list,time_)
    # getPrjMainDever()

    insertMainDevCross(getPrjList(),"2017_5")
    conn.close()
