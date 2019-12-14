# encoding:utf-8
from graphqlclient import GraphQLClient
import json
import redis
import pymysql
from datetime import datetime

db1 = pymysql.connect(host="127.0.0.1", user="root", passwd="123456", db="ossean_production", charset='utf8mb4',
                      cursorclass=pymysql.cursors.DictCursor, connect_timeout=3600)
db1.set_charset('utf8')
ver = db1.cursor()
db1.autocommit(1)
r = redis.Redis(host="127.0.0.1", port=6379, db=0)

insert_sql = "insert into github_issue_1(id,totalCount_issueclosed) VALUES (%d,%d)"
update_sql = "update osp_github_total set issue_flag = 1 where id = %d"
update_sql_no = "update osp_github_total set issue_flag = 2 where id = %d"

success_count = 0
starttime = datetime.now()
Max_Num = 6
def crawler():
	global success_count
	try:
		repo =r.spop("issues_set").decode('utf-8')
		repo_id = int(repo.split(" ")[0])
		repo_url = repo.split(" ")[1]
		owner=repo_url.split('/')[3]
		repo_name=repo_url.split("/")[4]

	except:
		pass
	else:
		stop_loop = False
		while(True):
			access_token = (r.rpop("access_token")).decode('utf-8')
			client = GraphQLClient('https://api.github.com/graphql')
			client.inject_token(access_token)
		
			# str_result='''
			# 	query{
            #
      		# 		repository(owner:"%s",name:"%s"){
          	# 			createdAt
			# 			forks{
			# 			  totalCount
			# 			}
			# 			watchers{
			# 			  totalCount
			# 			}
			# 			stargazers{
			# 			  totalCount
			# 				}
			# 			releases{
			# 				  totalCount
			# 			}
			# 				github_api(states:OPEN){
			# 				totalCount
			# 				}
			# 			milestones{
			# 				totalCount
			# 			}
		  	# 			}
			# 		}
			# 		'''

			str_issueforclosed='''
				query{
      				repository(owner:"%s",name:"%s"){
		  				github_api(states:CLOSED){
		  	   				totalCount		
		  					}
     					}
					}'''
			# result = client.execute(str_result%(owner,repo_name))

			for i in range(Max_Num):
				try:
					result = client.execute(str_issueforclosed % (owner, repo_name))
					break
				except:
					if i < Max_Num - 1:
						continue
					else:
						print 'URLError: <urlopen error timed out> All times is failed '




			# result_json = json.loads(result)
			result_json=json.loads(result)
			
			if (result_json["data"]==None or result_json["data"]["repository"]==None):
				if result_json["errors"][0]["type"]=="NOT_FOUND":
					ver.execute(update_sql_no % (repo_id)) #no result flag=2
					break
				elif result_json["errors"][0]["type"]=="RATE_LIMITED":#token valid
					continue
			else:
				temp_json=result_json["data"]["repository"]

				# created_at = str(temp_json["createdAt"])
				# totalCount_issueopen= 0 if  temp_json["github_api"]["totalCount"]==None else temp_json["github_api"]["totalCount"]
				# totalCount_release=0 if temp_json["releases"]["totalCount"]==None else temp_json["releases"]["totalCount"]
				# totalCount_milestone=0 if temp_json["milestones"]["totalCount"]==None else temp_json["milestones"]["totalCount"]
                #
				# totalCount_forks = 0 if temp_json["forks"]["totalCount"]==None else temp_json["forks"]["totalCount"]
				# totalCount_watches = 0 if temp_json["watchers"]["totalCount"] == None else temp_json["watchers"]["totalCount"]
				# totalCount_stars = 0 if temp_json["stargazers"]["totalCount"] == None else temp_json["stargazers"]["totalCount"]

				total_issueclosed=0 if temp_json["github_api"]["totalCount"]==None else temp_json["github_api"]["totalCount"]



				ver.execute(insert_sql % (repo_id,total_issueclosed))
				ver.execute(update_sql%(repo_id))
				db1.commit()
				stop_loop = True
				success_count += 1
				if success_count % 100 == 0:
					print(repo_id, total_issueclosed)
					endtime = datetime.now()
					print("handle %d cost %s" % (success_count, (endtime - starttime).seconds))
			if(stop_loop):
				break

while(True):
	crawler()







