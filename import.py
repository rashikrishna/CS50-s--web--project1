import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scopped_session, seessionmaker


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine=create_engine(os.getenv("DATA BASE_URL"))
db=scopped_session(sessionmaker(bind=engine))

def main():
    f=open(book.csv)
    data=csv.reader(f)

    #db.execute("CREATE TABLE book (isbn varchar(30) PRIMARY KEY, title varchar(100), author varchar(100), year varchar(10) )")
    db.execute("CREATE TABLE reviews (username varchar(50) PRIMARY KEY, review varchar(200), isbn varchar(30) REFERENCES book)")
    db.commit()
    db.execute("CREATE TABLE users (userid SERIAL PRIMARY KEY, username varchar(50), password varchar(50))")
    db.commit()




if __name__=="__main__":
    main()
