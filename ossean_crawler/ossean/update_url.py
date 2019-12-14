import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ossean_production',
                       charset='utf8mb4')

cur = conn.cursor()
select_sql = "select ossean_id, url, description from projects_ossean_local"
update_sql = "update projects_ossean_local set url = '%s',homepage='%s',long_name = '%s',description= '%s' where ossean_id = %s"

##| 1135077 | rubinius/rubinius
# | github|:|https://github.com/rubinius/rubinius
# | github|:|e6e455995af5b743cfeac77d446a95a2
# | github|:|The Rubinius Language Platform
cur.execute(select_sql)
repo_tuples = cur.fetchall()

github_str_len = len("https://api.github.com/repos/")
for repo in repo_tuples:
	ossean_id = repo[0]
	url = None if repo[1] is None else "github|:|https://github.com/"+repo[1][github_str_len:]
	homepage = None if repo[1] is None else  "https://github.com/"+repo[1][github_str_len:]
	long_name = None if repo[1] is None else repo[1][github_str_len:]
	desc = None if repo[2] is None else pymysql.escape_string("github|:|" + repo[2])

	cur.execute(update_sql % (url,homepage,long_name,desc,ossean_id))
conn.commit()
cur.close()
conn.close()






