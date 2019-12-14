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

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="zyr_github", charset='utf8mb4',
                       connect_timeout=3600)
conn.autocommit(1)
cur = conn.cursor()
issues_select = "select url,issue_number,repo_id from issues_comment_crawler where comment_tag=0"
pr_select="select url,pr_number,repo_id from pr_comment_crawler where comment_tag=0"

#2,551,590
redis_client.delete('zyr_comments_set')
def start():
    #logger.info("producer begin to work")
    print("producer begin to work")
    while True:
        cur.execute(issues_select)
        urls_added=cur.fetchall()
        len1=len(urls_added)
        for i in urls_added:
            redis_client.sadd("zyr_comments_set", "is %s %s %s" % (i[0], i[1], i[2]))
        cur.execute(pr_select)
        urls_added=cur.fetchall()
        len1+=len(urls_added)
        for i in urls_added:
            redis_client.sadd("zyr_comments_set", "pr %s %s %s" % (i[0], i[1], i[2]))
        if(len1>10000):
            time.sleep(3600)
        else:
            time.sleep(50)



if __name__ == "__main__":
    start()