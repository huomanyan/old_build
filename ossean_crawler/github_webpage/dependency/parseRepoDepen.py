# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import pymysql
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

conn = pymysql.connect(host="127.0.0.1", user="root", passwd="123456", db="zyr_github", charset='utf8mb4',
                       connect_timeout=3600)
cur = conn.cursor()
insert_sql = "insert ignore into repo_depen_parsepage_total(project_id, project_name_owner, crawler_url, depen_project_name_owner)" \
             " VALUES (%s,'%s','%s','%s')"
# depen_select_sql = "select id,name_owner from projects_400_id "\
#                 "where js_ruby_flag=0 and (language='javascript' or language='ruby')"
depen_select_sql = "select id,name_owner from projects_400_id where js_ruby_flag is null "#and second_language in ('ruby','javascript')
update_sql='update projects_400_id set js_ruby_flag=0 where id = %s'

def getDepen(prj,name_owner,url):
    web_data = requests.get(url)
    soup = BeautifulSoup(web_data.text, 'lxml')

    dependencies = soup.find_all('div',{"class":"Box mb-3"})
    doc_length = len(dependencies)
    for i in range(doc_length):
        child=soup.select('#dependencies > div:nth-of-type(%s)' % (i+3))[0]
        detail=child.find_all('div',{"class":"border-top Details js-details-container"})
        depen_length = len(detail)
        for j in range(0,depen_length):
            dependencies = soup.select('#dependencies > div:nth-of-type(%s) > div:nth-of-type(%s) > div > span > a' % (i+3,j+2))
            if len(dependencies)==0:
                continue
            depen_name_owner = dependencies[0].get('href')
            if depen_name_owner[0]=='/':
                depen_name_owner = depen_name_owner[1:]
            value = (int(prj),name_owner,url,depen_name_owner)
            print(value)
            cur.execute(insert_sql % value)
            #''.join(dependencies[0].get_text().strip().split())
    conn.commit()

def start():
    cur.execute(depen_select_sql)
    fetchall = cur.fetchall()
    for i in fetchall:
        prj_id = i[0]
        name_owner = i[1]
        url = "https://github.com/%s/network/dependencies" % name_owner
        getDepen(prj_id,name_owner,url)
        print("prj %s handle success" % prj_id)
        cur.execute(update_sql % prj_id)

if __name__ == "__main__":
    start()
