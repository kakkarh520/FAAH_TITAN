import socket
import threading
import tkinter as tk
from tkinter import simpledialog,filedialog
import os

HOST="127.0.0.1"
PORT=5555

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((HOST,PORT))

# LOGIN
root=tk.Tk()
root.withdraw()

username=simpledialog.askstring("FAAH","Username")
password=simpledialog.askstring("FAAH","Password",show="*")

client.recv(1024)
client.send(f"{username}:{password}".encode())
client.recv(1024)

# UI
app=tk.Tk()
app.title("FAAH PRO MAX")
app.geometry("900x600")

selected_user=None

sidebar=tk.Listbox(app,width=25)
sidebar.pack(side="left",fill="y")

chat=tk.Text(app,state="disabled")
chat.pack(fill="both",expand=True)

def add(msg):
    chat.config(state="normal")
    chat.insert("end",msg+"\n")
    chat.config(state="disabled")
    chat.see("end")

def select(e):
    global selected_user
    selected_user=sidebar.get(sidebar.curselection())

sidebar.bind("<<ListboxSelect>>",select)

bottom=tk.Frame(app)
bottom.pack(fill="x")

entry=tk.Entry(bottom)
entry.pack(side="left",fill="x",expand=True)

def send():
    if not selected_user: return
    msg=entry.get()
    client.send(f"TO:{selected_user}:{msg}".encode())
    entry.delete(0,"end")

tk.Button(bottom,text="Send",command=send).pack(side="right")

# IMAGE SEND
def send_image():
    if not selected_user: return
    path=filedialog.askopenfilename()

    if not path: return

    size=os.path.getsize(path)
    name=os.path.basename(path)

    client.send(f"IMG:{selected_user}:{name}:{size}".encode())

    with open(path,"rb") as f:
        client.sendall(f.read())

tk.Button(bottom,text="📎 Image",command=send_image).pack(side="right")

# RECEIVE
def receive():
    while True:
        try:
            data=client.recv(1024).decode()

            if data.startswith("USERS:"):
                users=data.replace("USERS:","").split(",")
                sidebar.delete(0,"end")
                for u in users:
                    if u!=username:
                        sidebar.insert("end",u)

            elif data.startswith("MSG:"):
                _,sender,msg,tick=data.split(":",3)
                add(f"{sender}: {msg} {tick}")

            elif data.startswith("IMG:"):
                _,sender,file=data.split(":")
                add(f"{sender} sent image: {file}")

        except:
            break

threading.Thread(target=receive,daemon=True).start()

app.mainloop()