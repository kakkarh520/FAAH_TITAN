from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
from cryptography.fernet import Fernet
import os, sqlite3, datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD="uploads"
os.makedirs(UPLOAD,exist_ok=True)

# ---------- SIGNAL STYLE ENCRYPTION ----------
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def encrypt(msg):
    return cipher.encrypt(msg.encode()).decode()

def decrypt(msg):
    return cipher.decrypt(msg.encode()).decode()

# ---------- DATABASE ----------
def db():
    return sqlite3.connect("chat.db",check_same_thread=False)

conn=db()
c=conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS messages(
user TEXT,msg TEXT,time TEXT,file TEXT)""")
conn.commit()

online=set()

# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload",methods=["POST"])
def upload():
    f=request.files["file"]
    path=os.path.join(UPLOAD,f.filename)
    f.save(path)
    return {"file":f.filename}

@app.route("/uploads/<name>")
def files(name):
    return send_from_directory(UPLOAD,name)

# ---------- SOCKET ----------
@socketio.on("join")
def join(user):
    online.add(user)
    emit("online",list(online),broadcast=True)

@socketio.on("typing")
def typing(data):
    emit("typing",data,broadcast=True,include_self=False)

@socketio.on("message")
def msg(data):

    user=data["user"]
    text=decrypt(data["msg"])
    file=data.get("file")

    time=str(datetime.datetime.now().strftime("%H:%M"))

    c.execute("INSERT INTO messages VALUES(?,?,?,?)",
              (user,text,time,file))
    conn.commit()

    emit("message",{
        "user":user,
        "msg":encrypt(text),
        "time":time,
        "file":file
    },broadcast=True)

if __name__=="__main__":
    socketio.run(app,host="0.0.0.0",port=5000)