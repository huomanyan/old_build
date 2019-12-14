#encoding:utf-8
import pymysql
from sklearn import preprocessing
conn =  pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ossean_production',
                       charset='utf8mb4')
#
# 4. 健康度
# 近6月issue平均修复时间（h,取反比）、issue的closed／total (百分比 API) (归一化)
# S_4_1 = repair_issue_num 每分钟修多少个
# S_4_2 = close_propotion
def calRepair():
    update_sql = "update ossean_metric_patch set repair_time_sea = %f where id = %d"
    select_sql = "select s4_issue_time,s4_issue_count from ossean_issues_repair_patch where id = %d"

    cur = conn.cursor()
    prj_tuples = getRepoUrlList()
    count = 0
    for prj in prj_tuples:
        cur.execute(select_sql % prj[0])
        tmp = cur.fetchone()

        issue_time = tmp[0]
        issue_count = tmp[1]

        result = 0 if issue_time==0 else float(issue_count)/issue_time
        count += 1
        cur.execute(update_sql % (result, prj[0]))
        if count % 100 == 0:
            conn.commit()
    conn.commit()
    cur.close()

def getRepoUrlList():
    cur = conn.cursor()
    select_sql = "select id from ossean_metric_zscore limit 20000,130000"
    cur.execute(select_sql)
    prj_tuples = cur.fetchall()
    print("repo length : %d" % len(prj_tuples))
    cur.close()
    return prj_tuples

# 2.活跃度
# commits/ pull requests : 近3个月的增量（归一化）
# S_2_1 = commits_inc/ contri_inc
def cal_active():
    update_sql = "update ossean_metric_patch set active_sea = %f where id = %d"
    select_commit_sql = "select s4 from ossean_commits_incre_patch where id = %d"
    select_contri_sql = "select s4 from ossean_contri_patch where id = %d"

    cur = conn.cursor()
    prj_tuples = getRepoUrlList()
    count = 0
    for prj in prj_tuples:
        cur.execute(select_commit_sql % prj[0])
        commits_num = cur.fetchone()[0]

        cur.execute(select_contri_sql % prj[0])
        contris_num = cur.fetchone()[0]

        unit_commits = 0 if contris_num==0 else float(commits_num)/contris_num
        count+=1
        cur.execute(update_sql % (unit_commits,prj[0]))
        if count % 100==0:
            conn.commit()
    conn.commit()
    cur.close()

# 3.团队健康度 (近3个月)
# 管理者administrator/代码贡献者contributor/评论参与者comment_par/ issue报告者issue_reporter
# S_3_1 = 持续贡献度 ( pre_contri_inc  & now_contri_inc ) / pre_contri_inc
# S_3_2 = 增长的贡献度 now_contri_inc - ( pre_contri_inc  & now_contri_inc ) / now_contri_inc
# S_3 = S_3_1 + S_3_2
def calPeople():
    update_sql = "update ossean_metric_patch set continue_people_contri_sea = %f,incre_people_contri_sea = %f where id = %d"
    select_sql = "select s3,s4,union34,diff43 from ossean_contri_patch where id = %d"

    cur = conn.cursor()
    prj_tuples = getRepoUrlList()
    count = 0
    for prj in prj_tuples:
        cur.execute(select_sql % prj[0])
        tmp = cur.fetchone()

        pre_num = tmp[0]
        now_num = tmp[1]
        union_num = tmp[2]
        incre_num = tmp[3]

        continue_contri = 0 if pre_num==0 else float(union_num)/pre_num
        incre_contri = 0 if now_num==0 else float(incre_num)/now_num
        count+=1
        cur.execute(update_sql % (continue_contri,incre_contri,prj[0]))
        if count % 100==0:
            conn.commit()
    conn.commit()
    cur.close()

import pandas as pd
from scipy.stats import zscore
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine

def final():
    #id, forks_total, watches_total, stars_total, relative_memos_total,
    #active_sea, watches_incre_sea, continue_people_contri_sea, incre_people_contri_sea, repair_time_sea, close_vs_open

    engine = create_engine("mysql+pymysql://root:111111@10.107.10.110:3306/ghtorrent_2017_5?charset=utf8")
    sql = "select * from ossean_metric limit 100"
    df = pd.read_sql(sql, conn)
    cols = ['active_sea', 'watches_incre_sea', 'continue_people_contri_sea', 'incre_people_contri_sea', 'repair_time_sea']
    for col in cols:
        df[col] = zscore(df[col])
    scaler = MinMaxScaler()
    df[cols] = scaler.fit_transform(df[cols])
    df.to_sql(con=engine, name="ossean_metric_zscore", if_exists='append', index=False)

def calOpenClose():
    update_sql = "update ossean_metric_1_first set issue_repair_ratio = %f where id = %d"
    select_sql = "select issue_close,issue_open from ossean_metric_1_first where id = %d"

    cur = conn.cursor()
    prj_tuples = getRepoUrlList()
    count = 0
    for prj in prj_tuples:
        cur.execute(select_sql % prj[0])
        fetchone = cur.fetchone()
        close_num = fetchone[0]
        open_num = fetchone[1]

        close_ratio = 0 if close_num==0 else float(close_num)/(open_num+close_num)


        count += 1
        cur.execute(update_sql % (close_ratio, prj[0]))
        if count % 100 == 0:
            conn.commit()
    conn.commit()
    cur.close()

def calScore(rank_type):

    engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/ossean_production?charset=utf8")
    sql = "select * from ossean_metric where category = '%s' " % rank_type
    df = pd.read_sql(sql, conn)

    norm_cols = ['forks_total', 'watches_total', 'stars_total', 'relative_memos_total','active_sea',
             'watches_incre_sea', 'continue_people_contri_sea', 'incre_people_contri_sea',
            'issue_repair_time_sea','issue_repair_ratio','contri_num_sea','issue_incre_sea']

    #归一化处理
    for col in norm_cols:
        df[col] = zscore(df[col])
    scaler = MinMaxScaler()
    df[norm_cols] = scaler.fit_transform(df[norm_cols])

    df['sonar_result'] = (df['active_sea'].values + df['issue_repair_time_sea'].values)/2

    # 1.影响力:
    # S_1_1 = forks_total + watches_total + stars_total
    # S_1_2 = relative_memos_total
    # S_1_3 = forks_num + watches_num + stars_num(近3个月增量)
    df['influ'] = ((df['forks_total'].values + df['watches_total'].values+df['stars_total'].values)/3
                   + df['relative_memos_total'].values
                   + df['watches_incre_sea'].values)/3

    # 2.活跃度:df['active_sea']
    df['activity'] = (df['active_sea'].values + df['issue_incre_sea'].values)/2
    # 3.团队健康度:
    df['team_healthy'] = (df['continue_people_contri_sea'].values + df['incre_people_contri_sea'].values + df['contri_num_sea'].values)/3
    # 4.项目健康度:
    df['repo_healthy'] = (df['issue_repair_time_sea'].values + df['issue_repair_ratio'].values + df['sonar_result'].values)/3

    df['influ'] = zscore(df['influ'])
    scaler = MinMaxScaler()
    df['influ'] = scaler.fit_transform(df['influ'].reshape(-1, 1))

    df['activity'] = zscore(df['activity'])
    scaler = MinMaxScaler()
    df['activity'] = scaler.fit_transform(df['activity'].reshape(-1, 1))

    df['team_healthy'] = zscore(df['team_healthy'])
    scaler = MinMaxScaler()
    df['team_healthy'] = scaler.fit_transform(df['team_healthy'].reshape(-1, 1))

    df['repo_healthy'] = zscore(df['repo_healthy'])
    scaler = MinMaxScaler()
    df['repo_healthy'] = scaler.fit_transform(df['repo_healthy'].reshape(-1, 1))

    #指标分数，归一化 & 缩放
    df['score_index'] = (df['influ'].values+df['activity'].values+df['team_healthy'].values+df['repo_healthy'].values)/4
    df['score_index'] = zscore(df['score_index'])
    scaler = MinMaxScaler()
    df['score_index'] = scaler.fit_transform(df['score_index'].reshape(-1,1))


    #乘以watches分数 归一化 & 缩放
    df['score'] = (df['score_index'].values + df['watches_total'].values)/2
    df['score'] = zscore(df['score'])
    scaler = MinMaxScaler()
    df['score'] = scaler.fit_transform(df['score'].reshape(-1,1))

    df = df.drop('issue_open',axis=1)
    df = df.drop('issue_close', axis=1)
    df = df.drop('category', axis=1)

    df.to_sql(con=engine, name="ossean_metric_norm_type", if_exists='append', index=False)

def normScore():
    engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/ossean_production?charset=utf8")
    sql = "select * from ossean_metric_norm_type"
    df = pd.read_sql(sql, conn)

    df['score_index'] = zscore(df['score_index'])
    scaler = MinMaxScaler()
    df['score_index'] = scaler.fit_transform(df['score_index'].reshape(-1,1))
    df.to_sql(con=engine, name="ossean_metric_norm_types", if_exists='append', index=False)

def normRanksScore():
    engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/ossean_production?charset=utf8")
    sql = "select * from ossean_ranks"
    df = pd.read_sql(sql, conn)

    df['score'] = zscore(df['score'])
    scaler = MinMaxScaler()
    df['score'] = scaler.fit_transform(df['score'].reshape(-1,1))
    df.to_sql(con=engine, name="ossean_ranks_1", if_exists='append', index=False)


if __name__ == "__main__":
    # cal_active()
    # calPeople()
    # calScore()
    rank_type_list = ['database', 'machine learning', 'testing tools']
    for rank_type in rank_type_list:
        calScore(rank_type)
    # final()
    conn.close()




