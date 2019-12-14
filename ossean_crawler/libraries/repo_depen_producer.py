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

# conn = MySQLdb.connect(host="10.107.10.110", user="root", passwd="111111", db="zyr_github", charset='utf8mb4',
#                        connect_timeout=3600)
conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="zyr_github", charset='utf8mb4',
                       connect_timeout=3600)
conn.autocommit(1)
cur = conn.cursor()

depen_select = "select id,name_owner from projects_400_id where depen_tag=0"

#2,551,590
redis_client.delete('repo_depen_set')
def start():
    logger.info("producer begains to work")

    cur.execute(depen_select)
    urls_added = cur.fetchall()
    for i in urls_added:
        redis_client.sadd("repo_depen_set", "%s %s" % (i[0], i[1]))

if __name__ == "__main__":
    start()