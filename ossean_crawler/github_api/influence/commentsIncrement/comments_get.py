# -*- coding: utf-8 -*-
from datetime import datetime
import pymysql
import time
import os
import json
from io import BytesIO
import pycurl
import redis
import judgeCondition


user = "root"
passwd = "123456"

# user = "root"
# passwd = "NUDTpdl@"


db1 = pymysql.connect(host="127.0.0.1", user=user, passwd=passwd, db="rankgithub", charset='utf8mb4',
                      cursorclass=pymysql.cursors.DictCursor, connect_timeout=3600)
db1.set_charset('utf8')
ver = db1.cursor()
db1.autocommit(1)
r = redis.Redis(host="127.0.0.1", port=6379, db=0)
format_pulls = "https://api.github.com/repos/%s/%s/comments?page=%d&&per_page=50&&access_token=%s"

insert_sql = "insert ignore into commentsIncrement" \
			 " values(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d) "
# update_sametable_sql="update Increment set ossean_id=%d,20171101=%d,20171001=%d," \
#                      "20170901=%d,20170801=%d,20170701=%d,20170601=%d,20170501=%d,20170401=%d,20170301=%d,20170201=%d,20170101=%d where ossean_id=%d"

update_sql = "update osp_github_match_filter set forks_flag = 1 where id = %d"
update_sql_no = "update osp_github_match_filter set forks_flag = 2 where id = %d"


success_count = 0
starttime = datetime.now()

def pulls_get():
    global success_count
    try:
        repo = r.spop("forks_set").decode('utf-8')
        repo_id = int(repo.split(" ")[0])
        repo_url = repo.split(" ")[1]
        owner = repo_url.split('/')[3]
        repo_name = repo_url.split("/")[4]

        print ("一次redis的一条sql查询")

        dataLeftFlag = 1
        pageNum = 1;

        f20171101 = 0
        f20171001 = 0
        f20170901 = 0
        f20170801 = 0
        f20170701 = 0
        f20170601 = 0
        f20170501 = 0
        f20170401 = 0
        f20170301 = 0
        f20170201 = 0
        f20170101 = 0
    except:
        pass
    else:

        while (True):
            access_token = (r.rpop("access_token")).decode('utf-8')
            it_url = format_pulls % (owner,repo_name, pageNum,access_token)
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

                r.sadd("forks_set", repo)
                break
            else:
                print("data get")
                insert_lan = response.getvalue()
                response.close()
                json_str = json.loads(insert_lan.decode('utf-8'))
                if json_str.__contains__("message"):
                    if json_str["message"]=="Not Found" or json_str["message"]=="Repository access blocked":
                        ver.execute(update_sql_no % repo_id)
                        break
                    elif  json_str["message"]=="Bad credentials" or "API rate limit" in json_str["message"] :
                        continue
                else:
                    if len(json_str) == 0:
                        ver.execute(insert_sql % (repo_id,0,0,0,0,0,0,0,0,0,0,0))
                        ver.execute(update_sql % (repo_id))
                        break

                    for js in json_str:

                        if (str(js['created_at']) > "2017-01-00T00:00:00Z"):
                            strCreatedtime = js['created_at']
#以月为单位
                            if strCreatedtime > "2017-11-01T00:00:00Z":
                                f20171101 += 1
                            if strCreatedtime > "2017-10-01T00:00:00Z":
                                f20171001 += 1
                            if strCreatedtime > "2017-09-01T00:00:00Z":
                                f20170901 += 1
                            if strCreatedtime > "2017-08-01T00:00:00Z":
                                f20170801 += 1
                            if strCreatedtime > "2017-07-01T00:00:00Z":
                                f20170701 += 1
                            if strCreatedtime > "2017-06-01T00:00:00Z":
                                f20170601 += 1
                            if strCreatedtime > "2017-05-01T00:00:00Z":
                                f20170501 += 1
                            if strCreatedtime > "2017-04-01T00:00:00Z":
                                f20170401 += 1
                            if strCreatedtime > "2017-03-01T00:00:00Z":
                                f20170301 += 1
                            if strCreatedtime > "2017-02-01T00:00:00Z":
                                f20170201 += 1
                            if strCreatedtime > "2017-01-01T00:00:00Z":
                                f20170101 += 1
                        else:
                            dataLeftFlag = 0
                            break;

                    print("20170101月份的",f20170101)

                    if (len(json_str) < 50):
                        dataLeftFlag = 0
                    if (dataLeftFlag == 0):
                        success_count += 1

                        try:
                            ver.execute(insert_sql % (repo_id, f20171101,f20171001,f20170901,f20170801,f20170701,f20170601,f20170501,f20170401,f20170301,f20170201,f20170101))
                        # except:
                        #     ver.execute(update_sametable_sql % (f20171101,f20171001,f20170901,f20170901,f20170901,
                        #                               f20170901,f20170901,f20170901,f20170901,f20170901,f20170901,repo_id))
                        finally:
                            ver.execute(update_sql % (repo_id))

                        if success_count % 100 == 0:
                            endtime = datetime.now()
                            print("handle %d cost %s" % (success_count, (endtime - starttime).seconds))
                            
                        break
                    pageNum += 1
                    print("第几页为：", pageNum)

while (True):
    pulls_get()
