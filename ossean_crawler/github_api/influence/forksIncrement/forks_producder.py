import redis
import logging
import pymysql
import time
r = redis.Redis(host="127.0.0.1",port=6379,db=0)
logger = logging.getLogger()
hdlr = logging.FileHandler("produce.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)

user = "root"
passwd = "123456"

# user = "root"
# passwd = "NUDTpdl@"

conn = pymysql.connect(host="127.0.0.1",user=user,passwd=passwd,db="rankgithub",charset='utf8mb4' )
#conn = pymysql.connect(host="127.0.0.1",user="root",passwd="a123456",db="gitlab",charset='utf8' )
conn.autocommit(1)
cursor = conn.cursor()
forks_select="select id,url from osp_github_match_filter where forks_flag is null"
r.delete('forks_set')
def start():
    logger.info("producer begains to work")
    while True:
        cursor.execute(forks_select)
        urls_added=cursor.fetchall()
        for i in urls_added:
            r.sadd("forks_set","%s %s"%(i[0],i[1]))
        time.sleep(10)



if __name__ == "__main__":
    start()