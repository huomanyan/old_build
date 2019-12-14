import redis
import logging
import MySQLdb
r = redis.Redis(host="127.0.0.1",port=6379,db=0)
logger = logging.getLogger()
hdlr = logging.FileHandler("produce.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)

conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="newpass",db="github",charset='utf8mb4' )
#conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="NUDTpdl@",db="zyr_github",charset='utf8mb4' )
conn.autocommit(1)
cursor = conn.cursor()
forks_select="select id,url from dapp_repos "
r.delete('projects_commits_set')
def start():
    logger.info("producer begains to work")
    while True:
       cursor.execute(forks_select)
       urls_added=cursor.fetchall()
       for i in urls_added:
          r.sadd("projects_commits_set","%s %s"%(i[0],i[1]))
    time.sleep(10)


if __name__ == "__main__":
    start()
