# encoding: utf-8
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
format_pulls = "https://api.github.com/repos/%s/%s?access_token=%s"
format_pull = "https://api.github.com/repos/pytorch/pytorch"
insert_sql = "insert ignore into api(repo_id,po_name,full_name,description,fork,created_at,homepage,stargazers_count,watchers_count,po_language,forks_count,default_branch,network_count,subscribers_count,license_name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

def star_get():
    try:
        repo = r.spop("project_issues1").decode('utf-8')
        repo_id = int(repo.split(" ")[0])
        repo_fullname = repo.split(" ")[1]
        owner = repo_fullname.split('/')[0]
        repo_name = repo_fullname.split("/")[1]
        print(owner)
    except:
        pass
    else:
        while (True):
            access_token = (r.rpop("access_token_zyr")).decode('utf-8')
            it_url = format_pulls % (owner,repo_name,access_token)
            #it_url = format_pull
            it_c = pycurl.Curl()
            it_c.setopt(it_c.URL, it_url)
            response = BytesIO()
            it_c.setopt(it_c.WRITEFUNCTION, response.write)
            it_c.setopt(it_c.CONNECTTIMEOUT, 50)
            it_c.setopt(it_c.TIMEOUT, 60)
            it_c.setopt(it_c.SSL_VERIFYPEER, 0)
            it_c.setopt(it_c.SSL_VERIFYHOST, 0)
            it_c.setopt(it_c.FOLLOWLOCATION, 5)

            print (it_url)
            try:
                it_c.perform()
            except Exception as e:
                print (e)
                r.sadd("star_set", repo)
                break
            else:
                print("data get")
                insert_lan = response.getvalue()
                response.close()
                json_str = json.loads(insert_lan.decode('utf-8'))
                if json_str.__contains__("message"):
                    if json_str["message"] == "Not Found" or json_str["message"] == "Repository access blocked":
                        #ver.execute(update_sql_no % repo_id)
                        break
                    elif json_str["message"] == "Bad credentials" or "API rate limit"or"Sorry. Your account was suspended." in json_str["message"]:
                        continue
                else:
                    #todo
                    # 所有的0改为 f20171101，以防新爬取的一页得到的为空值，覆盖了前面所有的
                    if len(json_str) == 0:
                        ver.execute(insert_sql % (repo_id, 0, 0, 0, 0, 0))
                        # ver.execute(update_sql % (repo_id))
                        break

                    po_name = json_str["name"]
                    full_name = json_str["full_name"]
                    description = json_str["description"]
                    fork = json_str["fork"]
                    created_at = json_str["created_at"]
                    homepage = json_str["homepage"]
                    stargazers_count = json_str["stargazers_count"]
                    watchers_count = json_str["watchers_count"]
                    po_language = json_str["language"]
                    forks_count = json_str["forks_count"]
                    default_branch = json_str["default_branch" ]
                    network_count = json_str["network_count"]
                    subscribers_count = json_str["subscribers_count"]
                    license = json_str["license"]
                    license_name = license["name"]
                    print(watchers_count)
                # 插入值并更新标志位
                ver.execute(insert_sql ,(repo_id,po_name,full_name,description,fork,created_at,homepage,stargazers_count,watchers_count,po_language,forks_count,default_branch,network_count,subscribers_count,license_name))
                # ver.execute(update_sql % (repo_id))

                break  # 跳出while循环，结束爬取该项目,


while(True):
    star_get()