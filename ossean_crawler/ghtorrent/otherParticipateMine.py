import pymysql
conn = pymysql.connect(host='10.107.10.110', port=3306, user='root', passwd='111111', db='ghtorrent_2017_5',
                       charset='utf8mb4')
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
def getPrjOtherParticipate(i):
    #804
    prj_list = getPrjList()
    insert_sql = "insert into project_other_participate(repo_id, user_id,time) VALUES (%s,%s,'%s')"
    # if i==0:
    #     select_pr_sql = "select id from pull_requests where base_repo_id = %d"
    #     select_pr_comments_sql = "select distinct user_id from pull_request_comments where created_at<='%s-01 00:00:00' " \
    #                     "and pull_request_id in %s"
    #     # issue
    #     select_issue_sql = "select id from github_api where repo_id = %d and created_at<= '%s-01 00:00:00'"
    #     select_issue_comment_sql  ="select distinct user_id from issue_comments where created_at < '%s-01 00:00:00' and issue_id in %s"
    # else:
    select_pr_sql = "select id from pull_requests where base_repo_id = %d"
    select_pr_comments_sql = "select distinct user_id from pull_request_comments where created_at<='%s-01 00:00:00' and created_at>'%s-01 00:00:00' " \
                             "and pull_request_id in %s"
    select_issue_sql = "select id from github_api where repo_id = %d and created_at<= '%s-01 00:00:00' and created_at>'%s-01 00:00:00'"
    select_issue_comment_sql = "select distinct user_id from issue_comments where created_at <= '%s-01 00:00:00' and created_at>'%s-01 00:00:00' and issue_id in %s"

    cur = conn.cursor()
    handled_count = 0
    for prj in prj_list:
        # pull request
        cur.execute(select_pr_sql % (prj))
        pr_tuples = cur.fetchall()
        pr_list = []
        for pr in pr_tuples:
            pr_list.append(pr[0])
        if len(pr_list) != 0:
            if len(pr_list) == 1:
                cur.execute(select_pr_comments_sql % (time_list[i],time_list[i-1],'(' + str(pr_list[0]) + ')'))
            else:
                cur.execute(select_pr_comments_sql % (time_list[i],time_list[i-1],str(tuple(pr_list))))
            pr_user_tuples = cur.fetchall()

            for user in pr_user_tuples:
                if user[0] is not None:
                    value = (int(prj), int(user[0]),pymysql.escape_string(time_list[i]+"-01 00:00:00"))
                    cur.execute(insert_sql % value)

        #issue
        cur.execute(select_issue_sql % (prj, time_list[i],time_list[i-1]))
        issue_tuples = cur.fetchall()
        issue_list = []
        for issue in issue_tuples:
            issue_list.append(issue[0])
        if len(issue_list) == 0:
            continue
        if len(issue_list) == 1:
            cur.execute(select_issue_comment_sql % (time_list[i],time_list[i-1], '(' + str(issue_list[0]) + ')'))
        else:
            cur.execute(select_issue_comment_sql % (time_list[i],time_list[i-1], str(tuple(issue_list))))
        issue_user_tuples = cur.fetchall()

        for user in issue_user_tuples:
            if user[0] is not None:
                value = (int(prj), int(user[0]), pymysql.escape_string(time_list[i] + "-01 00:00:00"))
                cur.execute(insert_sql % value)
        handled_count += 1
        if handled_count % 50 == 0:
            conn.commit()
            print("handled %d projects" % handled_count)
    conn.commit()
    print("handled %d projects" % handled_count)
    cur.close()

def insertOtherParticipateCross(time_index):
    prj_list = getPrjList()
    if time_index==0:
        insert_sql = 'insert into project_otherpar_cross_total_time (crossNum_%s,projectA,projectB) values (%s,%s,%s)'
    else:
        insert_sql = 'update project_otherpar_cross_total_time set crossNum_%s = %d where projectA = %d and projectB = %d'
    other_sql = "select DISTINCT user_id from project_other_participate where repo_id = %d and time <= '%s-01 00:00:00'"
    store = dict()

    cur = conn.cursor()
    for i in prj_list:
        cur.execute(other_sql % (i,time_list[time_index]))
        other_tuples = cur.fetchall()
        contributors_set = set() #存储other
        for j in other_tuples:
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

if __name__ == '__main__':
    for i in range(7):
        insertOtherParticipateCross(i)
    conn.close()
