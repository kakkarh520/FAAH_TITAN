from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_socketio import SocketIO, emit
import sqlite3, os, base64
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key="FAAH_OMEGA"

socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD="uploads"
os.makedirs(UPLOAD,exist_ok=True)

# ---------- DATABASE ----------
def db():
    return sqlite3.connect("database.db",check_same_thread=False)

def init():
    conn=db()
    c=conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT,
        photo TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        message TEXT,
        file TEXT,
        expire TEXT
    )""")

    conn.commit()
    conn.close()

init()

online=set()

# ---------- ENCRYPT ----------
def enc(m): return base64.b64encode(m.encode()).decode()
def dec(m): return base64.b64decode(m).decode()

# ---------- ROUTES ----------
@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["user"]
        p=request.form["pass"]

        conn=db()
        c=conn.cursor()
        try:
            c.execute("INSERT INTO users VALUES(?,?,?)",(u,p,""))
            conn.commit()
        except:
            pass

        session["user"]=u
        return redirect("/chat")

    return render_template("login.html")

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/")
    return render_template("chat.html",user=session["user"])

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
@socketio.on("connect")
def connect():
    if "user" in session:
        online.add(session["user"])
        emit("online",list(online),broadcast=True)

@socketio.on("disconnect")
def dis():
    if "user" in session:
        online.discard(session["user"])
        emit("online",list(online),broadcast=True)

@socketio.on("typing")
def typing(data):
    emit("typing",data,broadcast=True,include_self=False)

@socketio.on("send")
def send_msg(data):

    user=data["user"]
    msg=dec(data["msg"])
    file=data.get("file")

    expire=datetime.now()+timedelta(minutes=int(data["expire"]))

    conn=db()
    c=conn.cursor()
    c.execute("INSERT INTO messages(user,message,file,expire) VALUES(?,?,?,?)",
              (user,msg,file,str(expire)))
    conn.commit()

    emit("receive",{
        "user":user,
        "msg":enc(msg),
        "file":file,
        "time":datetime.now().strftime("%H:%M")
    },broadcast=True)

if __name__=="__main__":
    socketio.run(app,host="0.0.0.0",port=5000)