# -*- coding: utf-8 -*-
from datetime import datetime
import pymysql
import time
import os
import json
from io import BytesIO
import pycurl
import redis

db1 = pymysql.connect(host="127.0.0.1", user="root", passwd="123456", db="github", charset='utf8mb4',
                      cursorclass=pymysql.cursors.DictCursor, connect_timeout=3600)
db1.set_charset('utf8')
ver = db1.cursor()
db1.autocommit(1)
r = redis.Redis(host="127.0.0.1", port=6379, db=0)
format_forks = "https://api.github.com/repos/%s/%s?access_token=%s"

insert_sql = "insert into project_influ" \
			 "(id, forks, stars, watches)" \
			 " values(%d,%d,%d,%d)"
update_sql = "update projects_400_id set forks_flag = 1 where id = %d"
update_sql_no = "update projects_400_id set forks_flag = 2 where id = %d"

success_count = 0
starttime = datetime.now()

def forks_get():
    global success_count
    try:
        repo = r.spop("forks_set").decode('utf-8')
        repo_id = int(repo.split(" ")[0])
        repo_url = repo.split(" ")[1]
        owner = repo_url.split('/')[4]
        repo_name = repo_url.split("/")[5]

    except:
        pass
    else:
        stop_loop = False
        while (True):
            access_token = (r.rpop("access_token_zyr")).decode('utf-8')
            it_url = format_forks % (owner,repo_name, access_token)
            it_c = pycurl.Curl()
            it_c.setopt(it_c.URL, it_url)
            response = BytesIO()
            it_c.setopt(it_c.WRITEFUNCTION, response.write)
            it_c.setopt(it_c.CONNECTTIMEOUT, 30)
            it_c.setopt(it_c.TIMEOUT, 80)
            it_c.setopt(it_c.SSL_VERIFYPEER, 0)
            it_c.setopt(it_c.SSL_VERIFYHOST, 0)
            it_c.setopt(it_c.FOLLOWLOCATION, 5)
            try:
                it_c.perform()
            except:
                r.sadd("forks_set", repo)
                break
            else:
                insert_lan = response.getvalue()
                response.close()
                json_str = json.loads(insert_lan.decode('utf-8'))
                if json_str.__contains__("message"):
                    if json_str["message"]=="Not Found" or json_str["message"]=="Repository access blocked":
                        ver.execute(update_sql_no % repo_id)
                        break
                    elif  json_str["message"]=="Bad credentials":
                        continue
                else:
                    forks = int(json_str['forks_count'])
                    stars = int(json_str['stargazers_count'])
                    watchers = int(json_str['subscribers_count'])
                    # issues_open = int(json_str['open_issues_count'])
                    print (repo_id,forks,stars,watchers)
                    # ver.execute(insert_sql % (repo_id,issues_open,forks,stars,watchers))
                    ver.execute(insert_sql % (repo_id, forks,stars,watchers))
                    ver.execute(update_sql % (repo_id))
                    stop_loop = True
                    success_count += 1
                    if success_count % 100 == 0:
                        endtime = datetime.now()
                        print("handle %d cost %s" % (success_count,(endtime - starttime).seconds))

                if(stop_loop):
                    break

while (True):
    forks_get()
