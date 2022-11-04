import os
import json
import requests
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

message=('')

@app.route("/", methods=["POST", "GET"])
def index():
    message=("")
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        repassword=request.form.get("repassword")

        if repassword != password:
            message=("Password doesn't match")

        else:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password )",{"username":username, "password":password})
            db.commit()
            message=("Success! You can login now")
            return render_template("index.html",message=message)


    return render_template("index.html",message=message)


@app.route("/home",methods=["POST"])
def home():
    user=request.form.get("v_username")
    pwd=request.form.get("v_password")
    query=db.execute("SELECT * FROM users WHERE username=:user AND password=:pwd",{"user":user,"pwd":pwd}).fetchone()
    if query is None:
        message=("Username or Password Incorrect")
        return render_template("index.html",message=message)
    session["logged_user"]=user
    return render_template("home.html",user=session["logged_user"])

@app.route("/results", methods=["POST"])
def results():
    logged_user=session.get("logged_user")
    search=request.form.get("search")
    if db.execute("SELECT * from books WHERE author iLIKE '%"+search+"%' OR isbn iLIKE '%"+search+"%' OR title iLIKE '%"+search+"%' ",{"type":type,"search":search}).fetchone() is None:
        return render_template("results.html",res="No results Found")
    results=db.execute("SELECT * from books WHERE author iLIKE '%"+search+"%' OR isbn iLIKE '%"+search+"%' OR title iLIKE '%"+search+"%' ",{"type":type,"search":search}).fetchall()
    return render_template("results.html",results=results,user=logged_user)

#roue for book-details
@app.route("/isbn/<string:isbn>",methods=["POST","GET"])
def bookpage(isbn):
    logged_user=session.get("logged_user")
    err=("")
    review=db.execute("SELECT * FROM reviews where isbn=:isbn",{"isbn":isbn}).fetchall()
    book=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()

    # TODO: Use open libraty APIs, GR have deprecated their API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params= {"isbns":isbn, "key":"XMNPkrbVcr69QOm8TcPSwQ"})

    # Check if the response is valid.
    if res.status_code != 200:
        err = "Server authorization error"
        return render_template("book.html",book=book, err=err, review=review, user=logged_user, rating=0, count=0)

    data=res.json()["books"][0]["average_rating"]
    count=res.json()["books"][0]["work_ratings_count"]

    if request.method == "POST":
        if db.execute("SELECT * FROM reviews where username=:u AND isbn=:isbn",{"u":logged_user, "isbn":isbn}).fetchone() is None:
            new_review=request.form.get("review")
            rating=int(request.form.get("rating"))
            db.execute("INSERT INTO reviews (username, review, isbn, rating) VALUES (:a, :b, :c, :d)", {"a":logged_user, "c":isbn, "b":new_review, "d":rating})
            db.commit()
        else:
            review=db.execute("SELECT * FROM reviews where isbn=:isbn",{"isbn":isbn}).fetchall()
            err=("Only one review")

    return render_template("book.html",book=book, err=err, review=review, user=logged_user, rating=data, count=count)


#creating api
@app.route("/api/<isbn>")
def api(isbn):
    data=db.execute("SELECT * FROM books WHERE isbn= :isbn",{"isbn":isbn}).fetchone()
    if data is None:
        return jsonify({"success":False}), 404
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
