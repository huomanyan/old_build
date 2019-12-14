import redis
import logging
import time
r = redis.Redis(host="127.0.0.1",port=6379,db=0)

patch_size = 10000
print "token generate"
def start():
    while True:
        fopen = open("access_token1.txt", "r")
        token = []
        for i in fopen:
            token.append(i.replace("\n", ""))
        token_len = len(token)
        print(token_len)
        fopen.close()
        num_redis = r.llen("access_token_hmy")
        if(num_redis<patch_size):
            for jj in range(num_redis,patch_size+1000):
                r.lpush("access_token_hmy","%s"%(token[jj%token_len]))
        time.sleep(2)



if __name__ == "__main__":
    start()