# -*- coding: utf-8 -*-
import MySQLdb
import time
import os

import json
import cStringIO
import pycurl
import redis
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="github", charset='utf8mb4',
                       connect_timeout=3600)

conn.autocommit(1)
cur=conn.cursor()

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)

comment_url= "%s/issues/%s/comments?page=%s&&access_token=%s"

insert_sql= "insert ignore into issues_comments(repo_id,issue_number,comment_id,body,created_at,login,author_association,is_pr)" \
               " values(%s,%s,%s,'%s','%s','%s','%s',%s)"

update_issues="update issues_comment_crawler set comment_tag=1 where repo_id=%s and issue_number=%s "
update_pr="update pr_comment_crawler set comment_tag=1 where repo_id=%s and pr_number=%s"

update_issues_bad="update issues_comment_crawler set comment_tag=-1 where repo_id=%s and issue_number=%s "
update_pr_bad="update pr_comment_crawler set comment_tag=-1 where repo_id=%s and pr_number=%s"

def issues_get():
    try:
        name=redis_client.spop("zyr_comments_set")
        iss_tag=name.split(" ")[0]
        url=name.split(" ")[1]
        number=name.split(" ")[2]
        repo_id=name.split(" ")[3]
        page_num=1
        issues_tag = 1
    except:
        pass
    else:
        while (True):
            access_token = redis_client.rpop("access_token_zyr")
            it_url= comment_url % (url, number, page_num, access_token)
            it_c = pycurl.Curl()
            it_c.setopt(it_c.URL, it_url)
            it_b = cStringIO.StringIO()
            it_c.setopt(it_c.WRITEFUNCTION, it_b.write)
            it_c.setopt(it_c.CONNECTTIMEOUT, 30)
            it_c.setopt(it_c.TIMEOUT, 40)
            it_c.setopt(it_c.SSL_VERIFYPEER, 0)
            it_c.setopt(it_c.SSL_VERIFYHOST, 0)
            it_c.setopt(it_c.FOLLOWLOCATION, 5)
            try:
                it_c.perform()
            except:
                pass
            else:
                it_html = it_b.getvalue().decode("utf-8", "ignore")
                it_hhh = json.loads(it_html)
                it_b.close()
                if(type(it_hhh)==dict):
                    try:
                        if(it_hhh['message'][:3]=="API" or it_hhh['message'][:3]=="Bad"):#API :token次数限制 Bad:token失效
                            pass
                        else:#access failure Not Found
                            print it_hhh
                            print it_url
                            if (iss_tag == "pr"):
                                cur.execute(update_pr_bad % (repo_id,number))
                            if (iss_tag == "is"):
                                cur.execute(update_issues_bad % (repo_id,number))
                            break
                    except:
                        break
                elif(type(it_hhh)==list):
                    if(len(it_hhh)==0):
                        issues_tag=0
                    else:
                        if (len(it_hhh) < 30):
                            issues_tag = 0

                        for it_ii in it_hhh:
                            #repo_id, issue_number, comment_id, body, created_at, login, author_association
                            comment_id = it_ii["id"]
                            body = None if it_ii["body"] is None else MySQLdb.escape_string(it_ii["body"])
                            created_at = it_ii["created_at"]
                            login = it_ii["user"]["login"]
                            author_association = it_ii["author_association"]
                            if (iss_tag == "pr"):
                                is_pr = 1
                            elif (iss_tag == "is"):
                                is_pr = 0
                            cur.execute(insert_sql % (repo_id, number, comment_id,body, created_at, login,author_association,is_pr))
                    if(issues_tag==0):
                        if(iss_tag=="pr"):
                            cur.execute(update_pr % (repo_id,number))
                        if(iss_tag=="is"):
                            cur.execute(update_issues % (repo_id,number))
                        break
                    page_num+=1


while(True):
    issues_get()