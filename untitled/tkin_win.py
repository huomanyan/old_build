import tkinter as tk
import os
from tkinter import messagebox
from urllib.request import urlretrieve
import sys
import requests
import socket
import urllib3
from requests.adapters import HTTPAdapter
#import fin

# 屏蔽warning信息
#requests.packages.urllib3.disable_warnings()
def download_file(url, file_path):
# 第一次请求,得到文件总大小
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    try:
        r1 = s.get(url, stream=True, verify=False,timeout=20)
    except (requests.exceptions.ConnectionError,requests.exceptions.RequestException,socket.timeout,urllib3.exceptions.ReadTimeoutError) as err:
        return
    total_size = int(r1.headers['Content-Length'])

# 查看本地文件下载了多少
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0
    # 显示一下下载了多少
    print(temp_size)
    print(total_size)
    # 从本地文件已经下载过的后面下载
    headers = {'Range': 'bytes=%d-' % temp_size}
    # 重新请求网址，加入新的请求头的
    r = requests.get(url, stream=True, verify=False, headers=headers,timeout=5)

    # "ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        try:
            for chunk in r.iter_content(chunk_size=1024):

                temp_size = os.path.getsize(file_path)
                f.write(chunk)
                f.flush()

                ###下载实现进度显示####
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
                temp_size = os.path.getsize(file_path)
                if temp_size>total_size:
                    return temp_size,total_size
                    break
        except (requests.exceptions.ConnectionError,requests.exceptions.RequestException,socket.timeout,urllib3.exceptions.ReadTimeoutError) as err:
            return
    print()  # 避免上面\r 回车符
