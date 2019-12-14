import redis
import time
r = redis.Redis(host="127.0.0.1",port=6379,db=0)

patch_size = 10000
print (11)
def start():
    while True:
        fopen = open("access_token.txt", "r")
        token = []
        for i in fopen:
            token.append(i.replace("\n", ""))
        token_len = len(token)
        fopen.close()
        num_redis = r.llen("access_token")
        if(num_redis<patch_size):
            for jj in range(num_redis,patch_size+1000):
                r.lpush("access_token","%s"%(token[jj%token_len]))
        time.sleep(2)

if __name__ == "__main__":
    start()