# coding: UTF-8
import requests
url="http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz"
path="D:/img/t10k-images-idx3-ubyte.gz"
r=requests.get(url)
print("ok")
with open(path,"wb") as f:
    f.write(r.content)
f.close()