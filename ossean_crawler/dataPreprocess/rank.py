#encoding:utf-8
import pymysql
conn =  pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ossean_production',
                       charset='utf8mb4')
# Machine Learning：
#<deep-learning>,<machine-learning>,<machine learning>,<neural-network>

# Database
#<sql>,<database>

# Cloud Computing
# <cloud>
#todo:
#把ossean的原始项目也要插入到排行榜中，新增字段from判断，排序根据帖子数量类比

cur = conn.cursor()

rank_type_list= ['database','machine learning','testing tools']
select_sql = "select id,score,relative_memos_num from ossean_ranks_type where rank_type = '%s' order by score desc"
update_sql = "update ossean_ranks_type set rank =%d where id = %d"

for rank_type in rank_type_list:
    cur.execute(select_sql % rank_type)
    fetchall = cur.fetchall()
    rank = 0
    for i in fetchall:
        id = i[0]
        rank = rank+1
        cur.execute(update_sql % (rank,id))
    conn.commit()

cur.close()
conn.close()

