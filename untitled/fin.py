import tkinter as tk
import pickle
#import tkin_win
import os
import requests
import socket
import urllib3
from requests.adapters import HTTPAdapter
import text

window = tk.Tk()
window.title('Welcome to Mofan Python')
window.geometry('450x300')

# welcome image
canvas = tk.Canvas(window, height=200, width=500)
image_file = tk.PhotoImage(file='welcome.gif')
image = canvas.create_image(0,0, anchor='nw', image=image_file)
canvas.pack(side='top')

# user information
tk.Label(window, text='dataset url: ').place(x=50, y= 150)
tk.Label(window, text='filename: ').place(x=50, y= 190)

var_usr_url = tk.StringVar()
#var_usr_name.set('example@python.com')
entry_usr_url = tk.Entry(window, textvariable=var_usr_url)
entry_usr_url.place(x=160, y=150)
var_usr_name = tk.StringVar()
entry_usr_name = tk.Entry(window, textvariable=var_usr_name)#, show='*')
entry_usr_name.place(x=160, y=190)

def usr_login():
    usr_url = var_usr_url.get()
    usr_name = var_usr_name.get()
    os.makedirs('D:/img/', exist_ok=True)  # 创建目录存放文件
    #return (usr_name,usr_pwd)
    print(usr_url,usr_name)
    temp = 0
    total = 1
    while(temp<total):

        try:
            text.download(usr_url, 'D:/img/%s' % usr_name)
            temp, total = text.download(usr_name, 'D:/img/%s' % usr_name)

        except (TypeError,requests.exceptions.ConnectionError, requests.exceptions.RequestException, socket.timeout,
                urllib3.exceptions.ReadTimeoutError) as err:
            continue
            #tk.messagebox.showinfo(message='Your dataset download has been interrupted!Please click again')
         #   break'''
    tk.messagebox.showinfo(message='Your dataset has been downloaded!')
''''''





# login and sign up button
btn_login = tk.Button(window, text='Login', command=usr_login)
btn_login.place(x=170, y=230)
#btn_sign_up = tk.Button(window, text='Sign up', command=usr_sign_up)
#btn_sign_up.place(x=270, y=230)

window.mainloop()