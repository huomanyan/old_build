# -*- coding: utf-8 -*-
import MySQLdb
import time
import os
import json
import cStringIO
import pycurl
import redis
import MySQLdb.cursors

conn = MySQLdb.connect(host="10.107.10.110", user="root", passwd="111111", db="zyr_github", charset='utf8', cursorclass=MySQLdb.cursors.DictCursor, connect_timeout=3600)

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)

conn.autocommit(1)
conn.set_character_set('utf8')
cur=conn.cursor()

format_issues="%s/issues?page=%s&&access_token=%s&&per_page=100&&state=all"

updated_repo_success = "update projects_783 set finish_tag=1 where id=%s"
updated_repo_error= "update projects_783 set finish_tag=-1 where id=%s"


insert_issues= "insert ignore into issues(id,repo_id,issue_number,main) values(%s,%s,%s,%s)"
insert_pr= "insert ignore into pull_request(id,repo_id,pr_number,main) values(%s,%s,%s,%s)"



def issues_get():
    repo=redis_client.spop("project_issues")
    repo_id=repo.split(" ")[0]
    url=repo.split(" ")[1]
    page_num=1
    issues_tag = 1

    # cur.execute(select_time, (repo_id, url))
    while (True):
        access_token = redis_client.rpop("access_token_zyr")
        it_url=format_issues%(url,page_num,access_token)
        it_c = pycurl.Curl()
        it_c.setopt(it_c.URL, it_url)
        it_b = cStringIO.StringIO()
        it_c.setopt(it_c.WRITEFUNCTION, it_b.write)
        it_c.setopt(it_c.CONNECTTIMEOUT, 60)
        it_c.setopt(it_c.TIMEOUT, 80)
        it_c.setopt(it_c.SSL_VERIFYPEER, 0)
        it_c.setopt(it_c.SSL_VERIFYHOST, 0)
        it_c.setopt(it_c.FOLLOWLOCATION, 5)
        try:
            it_c.perform()
        except Exception as ee:
            print ee
            pass
        else:
            it_html = it_b.getvalue().decode("utf-8", "ignore")
            it_hhh = json.loads(it_html)
            it_b.close()

            if (type(it_hhh) == dict):
                try:
                    if (it_hhh['message'][:3] == "API" or it_hhh['message'][:3] == "Bad"):  # API :token次数限制 Bad:token失效
                        pass
                    else:  # access failure
                        cur.execute(updated_repo_error % (repo_id))
                        break
                except:
                    break
            elif(type(it_hhh)==list):
                if(len(it_hhh)==0):
                    issues_tag=0
                else:
                    if (len(it_hhh) < 100):
                        issues_tag = 0
                    for it_ii in it_hhh:
                        number = it_ii['number']
                        main = str(it_ii)
                        id = it_ii['id']
                        if 'pull_request' in it_ii:
                            cur.execute(insert_pr,(id,repo_id,number,main))
                        else:
                            cur.execute(insert_issues, (id, repo_id, number, main))
                page_num += 1
            if(issues_tag==0):
                break
    if issues_tag == 0 :
        cur.execute(updated_repo_success % repo_id)
        print("%s crawler success" % repo_id)
    conn.commit()

while(True):
    issues_get()