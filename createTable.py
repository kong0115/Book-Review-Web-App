import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

"""
A program that create 3 tables in the database to keep track of books, users, and reviews respectively.
"""

def main():
    #create a table to keep track of books
    db.execute("CREATE TABLE books (isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL)")
    #create a table to keep track of users
    db.execute("CREATE TABLE users (username VARCHAR PRIMARY KEY, fullName VARCHAR NOT NULL, email VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    #create a table to keep track of reviews
    db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, text VARCHAR NOT NULL, rating INTEGER NOT NULL, user_id VARCHAR REFERENCES users, book_id VARCHAR REFERENCES books)")
    db.commit()

if __name__ == "__main__":
    main()
