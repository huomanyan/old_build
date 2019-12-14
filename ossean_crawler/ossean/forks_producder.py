import redis
import logging
import pymysql
r = redis.Redis(host="127.0.0.1",port=6379,db=0)
logger = logging.getLogger()
hdlr = logging.FileHandler("produce.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)

# conn = pymysql.connect(host="127.0.0.1",user="root",passwd="123456",db="ossean_production",charset='utf8mb4' )
conn = pymysql.connect(host="10.107.10.110",user="root",passwd="111111",db="zyr_github",charset='utf8mb4' )
conn.autocommit(1)
cursor = conn.cursor()
forks_select="select id,url from projects_400_id where forks_flag = 0"
# r.delete('forks_set')
def start():
    logger.info("producer begains to work")

    cursor.execute(forks_select)
    urls_added=cursor.fetchall()
    for i in urls_added:
        r.sadd("forks_set","%s %s"%(i[0],i[1]))

if __name__ == "__main__":
    start()