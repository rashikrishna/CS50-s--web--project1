import os

from flask import Flask, session, render_template,request, url_for,redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

message=""


@app.route("/")
def index():
    return render_template("index.html",message=message)

#defining register
def register():
    username=request.form.get("username")
    password=request.form.get("password")
    repassword=request.form.get("repassword")

    if repassword!=password:
        message="Password doesn't match"


@app.route("/home",methods=["POST"])
def home():
    user=request.form.get("v_username")
    pwd=request.form.get("v_password")
    query=db.execute("SELECT userid FROM users WHERE username=:user AND password=:pwd",{"user":user,"pwd":pwd}).fetchone()
    if query is None:
        message="Username or Password Incorrect"
        return redirect(url_for("index"))
    return render_template("home.html",user=query.userid)

@app.route("/results", methods=["POST"])
def results():
    search=request.form.get("search")
    results=db.execute("SELECT * from books WHERE author iLIKE '%"+search+"%' OR isbn iLIKE '%"+search+"%' OR title iLIKE '%"+search+"%' ",{"type":type,"search":search}).fetchall()
    return render_template("results.html",results=results)


#creating api
@app.route("/api/<isbn>")
def api(isbn):
    data=db.execute("SELECT * fROM books where isbn=:a ",{"a":isbn}).fetchall()
    return jsonify ({
        "isbn":data.isbn,
        "title":data.title,
        "author":data.author,
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))



if __name__=="__main__":
	app.run(port=5000)
