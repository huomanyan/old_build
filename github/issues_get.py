# -*- coding: utf-8 -*-
import MySQLdb
import time
import os
import json
import cStringIO
import pycurl
import redis
import MySQLdb.cursors

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="github", charset='utf8', cursorclass=MySQLdb.cursors.DictCursor, connect_timeout=3600)

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)

conn.autocommit(1)
conn.set_character_set('utf8')
cur=conn.cursor()

format_issues="https://api.github.com/repos/%s/%s/issues?page=%s&&per_page=100&&state=all&&access_token=%s"
#format_issues="https://api.github.com/repos/pytorch/pytorch/issues?page=%s&&per_page=100&&state=all"

insert_issues= "insert ignore into issues(id,repo_id,title,issue_number,state,comments,created_at,updated_at,closed_at,body) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
insert_pr= "insert ignore into pull_request(id,repo_id,title,issue_number,state,comments,created_at,updated_at,closed_at,body) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

updated_repo_issuenum = "update api set issues_num=%s where repo_id=%s"

def issues_get():
    repo=redis_client.spop("project_issues")
    if repo is None:
        time.sleep(86000)
        return
    #repo = redis_client.spop("project_issues")
    repo_id=repo.split(" ")[0]
    repo_fullname=repo.split(" ")[1]
    current_num=int(repo.split(" ")[2])
    print(repo_id,repo_fullname)
    owner = repo_fullname.split('/')[0]
    repo_name = repo_fullname.split("/")[1]
    print(owner)
    print(type(current_num))
    page_num=1
    issues_tag = 1
    max_num = 0

    # cur.execute(select_time, (repo_id, url))
    while (True):
        access_token = redis_client.rpop("access_token_hmy")
        it_url=format_issues%(owner,repo_name,page_num,access_token)
        #it_url = format_issues%(page_num,access_token)

        print(page_num)
        #pycurl部分，执行网络操作。通过URL检索资源
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
                        issue_number = it_ii['number']

                        if(issue_number > current_num):
                            main = str(it_ii)
                            id = it_ii['id']
                            print(id)
                            title = it_ii['title']
                            state = it_ii["state"]
                            comments = it_ii["comments"]
                            created_at = None if it_ii["created_at"] is None else it_ii["created_at"]
                            updated_at = None if it_ii["updated_at"] is None else it_ii["updated_at"]
                            closed_at = None if it_ii["closed_at"] is None else it_ii["closed_at"]
                            body = it_ii["body"]
                            if('pull_request' in it_ii):
                                cur.execute(insert_pr, (
                                id, repo_id, title, issue_number, state, comments, created_at, updated_at, closed_at,
                                body))
                            else:
                                cur.execute(insert_issues, (
                                id, repo_id, title, issue_number, state, comments, created_at, updated_at, closed_at,
                                body))
                            if (max_num < issue_number):
                                max_num = issue_number
                        else:
                            issues_tag = 0
                page_num += 1
            if(issues_tag==0):
                break
    if issues_tag == 0 :
        #cur.execute(updated_repo_success % repo_id)
        print("%s crawler success" % repo_id)
        current_num = max_num
        print(current_num)
        cur.execute(updated_repo_issuenum%(current_num,repo_id))
    conn.commit()

while(True):
    issues_get()
    #time.sleep(60)