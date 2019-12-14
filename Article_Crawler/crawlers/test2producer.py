import pymysql
import datetime
import logging
import redis
import time

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)
conn = pymysql.connect("localhost", "root", "123456", "ossean")
logger = logging.getLogger()
hdlr = logging.FileHandler("produce.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = conn.cursor()
conn.autocommit(1)
now = datetime.datetime.now()


select_osp= "select id,name from open_source_projects_copy1"
cursor.execute(select_osp)

def start():
    redis_client.delete("osp_id")
    logger.info("producer begains to work")
    cursor.execute(select_osp)
    fetchall = cursor.fetchall()
    for repo in fetchall:
        redis_client.sadd("osp_id", "%s %s"%(repo[0],repo[1]))
    i=redis_client.scard("osp_id")
    print(i)


if __name__ == "__main__":
    while(1):
        start()
        time.sleep(300)


