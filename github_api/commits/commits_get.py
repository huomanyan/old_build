#-*- coding: utf-8 -*-
import MySQLdb
import time
import os
import json
import cStringIO
import pycurl
import redis

conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="123456",db="github",charset='utf8' )
# conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="NUDTpdl@", db="zyr_github", charset='utf8mb4')

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)

conn.autocommit(1)
conn.set_character_set('utf8')
cur=conn.cursor()

format_commits= "https://api.github.com/repos/%s/%s/commits?page=%s&&per_page=100&&access_token=%s"

updated_repo_success = "update projects_783 set commit_tag=1 where id=%s"
updated_repo_error= "update projects_783 set commit_tag=-1 where id=%s"


insert_commits= "insert ignore into commits(repo_id,author, author_date, committer,commit_date,sha) values(%s,%s,%s,%s,%s,%s)"


def commits_get():
    repo=redis_client.spop("projects_commits_set")
    repo_id=repo.split(" ")[0]
    url=repo.split(" ")[1]
    owner = url.split('/')[3]
    repo_name = url.split("/")[4]

    pageNum=1
    commits_tag = 1

    # cur.execute(select_time, (repo_id, url))
    while (True):
        access_token = redis_client.rpop("access_token_zyr")
        it_url= format_commits % (owner,repo_name, pageNum,access_token)
        it_c = pycurl.Curl()
        it_c.setopt(it_c.URL, it_url)
        it_b = cStringIO.StringIO()
        it_c.setopt(it_c.WRITEFUNCTION, it_b.write)
        it_c.setopt(it_c.CONNECTTIMEOUT, 60)
        it_c.setopt(it_c.TIMEOUT, 80)
        it_c.setopt(it_c.SSL_VERIFYPEER, 0)
        it_c.setopt(it_c.SSL_VERIFYHOST, 0)
        it_c.setopt(it_c.FOLLOWLOCATION, 5)
        print (it_url)
        try:
            it_c.perform()
        except Exception as ee:
            print ee
            pass
        else:
            it_html = it_b.getvalue().decode("utf-8","ignore")

            it_hhh = json.loads(it_html)
            it_b.close()

            if (type(it_hhh) == dict):
                try:
                    if (it_hhh['message'][:3] == "API" or it_hhh['message'][:3] == "Bad"):  # API :token次数限制 Bad:token失效
                        pass
                    else:  # access failure
                        #cur.execute(updated_repo_error % (repo_id))
                        break
                except:
                    break
            elif(type(it_hhh)==list):
                if(len(it_hhh)==0):
                    commits_tag=0
                else:
                    if (len(it_hhh) < 100):
                        commits_tag = 0
                    for it_ii in it_hhh:
                        #repo_id,created_at,login,sha
                        sha = None if it_ii['sha'] is None else it_ii['sha']
                        author_date =None if it_ii["commit"]["author"]["date"] is None else it_ii["commit"]["author"]["date"]
                        if it_ii["author"]==None:
                            author = None
                        else:
                            if 'login' in it_ii["author"]:
                                author = it_ii["author"]["login"]
                            else:
                                author = None
                                print url,sha
                        if it_ii["committer"]==None:
                            # print url,sha
                            committer = None
                        else:
                            if 'login' in it_ii["committer"]:
                                committer = it_ii["committer"]["login"]
                                commit_date=None if it_ii["commit"]["committer"]["date"] is None else it_ii["commit"]["committer"]["date"]
                            else:
                                committer = None
                                print url,sha
                        cur.execute(insert_commits, (repo_id,author, author_date, committer,commit_date,sha))
                    pageNum += 1
            if(commits_tag==0):
                break
    if commits_tag == 0 :
        #cur.execute(updated_repo_success % repo_id)
        print("%s crawler success" % repo_id)
    conn.commit()

while(True):
    commits_get()