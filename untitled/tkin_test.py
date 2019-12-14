import tkinter as tk
import os
import urllib
from tkinter import messagebox
from urllib.request import urlretrieve

window = tk.Tk()
window.title('Welcome to Mofan Python')
window.geometry('450x300')

# welcome image
canvas = tk.Canvas(window, height=200, width=500)
image_file = tk.PhotoImage(file='welcome.gif')
image = canvas.create_image(0,0, anchor='nw', image=image_file)
canvas.pack(side='top')

# user information
tk.Label(window, text='url: ').place(x=50, y= 150)
tk.Label(window, text='name: ').place(x=50, y= 190)

var_usr_url = tk.StringVar()
#var_usr_url.set('example@python.com')
entry_usr_url = tk.Entry(window, textvariable=var_usr_url)
entry_usr_url.place(x=160, y=150)
var_usr_name = tk.StringVar()
entry_usr_name = tk.Entry(window, textvariable=var_usr_name)#, show='*')
entry_usr_name.place(x=160, y=190)

def auto_down(url,filename):
    try:
        urlretrieve(url,filename)
    except urllib.error.ContentTooShortError as err:
        print ("Network conditions is not good.Reloading.")
        auto_down(url,filename)


def usr_login():
    usr_url = var_usr_url.get()
    usr_name = var_usr_name.get()
    os.makedirs('D:/img/', exist_ok=True)  # 创建目录存放文件
    image_url = usr_url
    #print(image_url)
    return image_url,usr_name
    print(image_url,usr_name)
    #auto_down(image_url, 'D:/img/%s' % usr_name)  # 将什么文件存放到什么位置
    tk.messagebox.showinfo(message='Your dataset has been downloaded!')


# login and sign up button
btn_login = tk.Button(window, text='commit', command=usr_login)
url,name =usr_login()
print(url,name)
btn_login.place(x=170, y=230)


window.mainloop()