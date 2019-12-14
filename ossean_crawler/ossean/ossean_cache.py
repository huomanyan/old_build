import pymysql
import redis
import time
conn = pymysql.connect(host='172.16.128.30', port=3306, user='backup', passwd='NUDTpdl@123', db='ossean_production',
					   charset='utf8mb4')
# conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ossean_production',
# 					   charset='utf8mb4')
redis_ = redis.Redis(host="127.0.0.1",port=6379,db=0)


def updateMemosNum():

    select_memos_num_sql = "select count(*) from relative_memos"
    cur = conn.cursor()
    count = 0
    while(True):
        cur.execute(select_memos_num_sql)
        fetchone = cur.fetchone()
        memos_num = fetchone[0]
        count+=1
        # print "the %d time memos is %d" % (count,memos_num)
        # print redis_.set("memos",memos_num)
        time.sleep(30)
        conn.commit()


if __name__ == "__main__":
    updateMemosNum()




