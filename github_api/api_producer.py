import redis
import logging
import MySQLdb
import time
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)
logger = logging.getLogger()

hdlr = logging.FileHandler("produce.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)

conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="123456",db="github",charset='utf8')
# conn = MySQLdb.connect(host="192.168.80.104",user="influx",passwd="influx1234",db="gitlab",charset='utf8' )
conn.autocommit(1)
cursor = conn.cursor()
issues_select="select id,url from dapp_repos"
redis_client.delete("project_issues")


def start():
    logger.info("producer begains to work")
    while True:
        cursor.execute(issues_select)
        fetchall = cursor.fetchall()
        for repo in fetchall:
            redis_client.sadd("project_issues", "%s %s" % (repo[0], repo[1]))
            redis_client.sadd("project_issues1", "%s %s" % (repo[0], repo[1]))
        time.sleep(10)

if __name__ == "__main__":
    start()