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

# conn = MySQLdb.connect(host="10.107.10.110", user="root", passwd="111111", db="zyr_github", charset='utf8mb4',
#                        connect_timeout=3600)
conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="zyr_github", charset='utf8mb4',
                       connect_timeout=3600)

conn.autocommit(1)
cur=conn.cursor()

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)

# https://libraries.io/api/github/moment/moment/dependencies?api_key=be136d89c120a8fe4d5c039ece67f480
depend_url= "https://libraries.io/api/github/%s/%s/dependencies?api_key=%s"
repo_url="https://libraries.io/api/github/%s?api_key=%s"

insert_sql= "insert ignore into repositories_dependency(project_id,fullname, depen_prj_name,depen_name, depen_platform, depen_kind) " \
            "VALUES (%s,'%s','%s','%s','%s','%s')"

update_depend_sql="update projects_400_id set depen_tag=1 where id=%s"
update_depend_error_sql="update projects_400_id set depen_tag=-1 where id=%s"

update_repo_sql="update projects_400_id set license='%s' where id=%s"

def depens_get():
    repo=redis_client.spop("repo_depen_set")
    repo_id=repo.split(" ")[0]
    url=repo.split(" ")[1]

    owner = url.split('/')[4]
    repo_name = url.split("/")[5]

    # page_num=1
    depens_tag = 0

    # cur.execute(select_time, (repo_id, url))
    while (True):
        access_token = redis_client.rpop("access_token_zyr")
        it_url= depend_url % (owner, repo_name, access_token)
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
            result_json = json.loads(it_html)
            it_b.close()

            if result_json.has_key("error"):
                if "403" in result_json["error"]:# key 每分钟60条
                    continue
            elif result_json.has_key("message"):
                if "RecordNotFound" in result_json["message"]:
                    print("repo %s:%s not exist" % (repo_id,url))
                    depens_tag = -1
                    break
            else:
                #project_id,fullname, depen_prj_name,depen_name, depen_platform, depen_kind
                fullname = result_json["full_name"]
                dependencies = result_json["dependencies"]
                if len(dependencies) == 0:
                    print("repo %s : %s has no dependency!" % (repo_id,fullname))
                else:
                    print("repo %s has %s dependency" % (repo_id,len(dependencies)))
                    for depen in dependencies:
                        project_name = depen["project_name"]
                        name = depen['name']
                        platform = depen["platform"]
                        kind = depen["kind"]
                        cur.execute(insert_sql % (repo_id,MySQLdb.escape_string(fullname),MySQLdb.escape_string(project_name),MySQLdb.escape_string(name),platform,kind))
                    conn.commit()
                depens_tag = 1
                break

    if depens_tag == 1 :
        cur.execute(update_depend_sql % repo_id)
    if depens_tag == -1 :
        cur.execute(update_depend_error_sql % repo_id)

def license_get():
    repo = redis_client.spop("repo_depen_set")
    repo_id = repo.split(" ")[0]
    name_owner = repo.split(" ")[1]

    depens_tag = 0

    # cur.execute(select_time, (repo_id, url))
    while (True):
        access_token = redis_client.rpop("access_token_zyr")
        it_url = repo_url % (name_owner, access_token)
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
            result_json = json.loads(it_html)
            it_b.close()

            if result_json.has_key("error"):
                if "403" in result_json["error"]:  # key 每分钟60条
                    continue
            elif result_json.has_key("message"):
                if "RecordNotFound" in result_json["message"]:
                    print("repo %s:%s not exist" % (repo_id, name_owner))
                    depens_tag = -1
                    break
            else:
                # project_id,fullname, depen_prj_name,depen_name, depen_platform, depen_kind
                repo_license = result_json["license"]
                if repo_license is None:
                    print("repo %s : %s has no license" % (repo_id, repo_license))
                else:
                    # print("repo %s has %s license" % (repo_id, repo_license))
                    cur.execute(update_repo_sql % (repo_license,repo_id))
                    conn.commit()
                depens_tag = 1
                break

    if depens_tag == 1:
        cur.execute(update_depend_sql % repo_id)
    if depens_tag == -1:
        cur.execute(update_depend_error_sql % repo_id)
while(True):
    license_get()