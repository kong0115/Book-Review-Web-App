import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

"""
A program that imports books data in CSV format to the database.
"""

def main():
    f = open("books.csv") #open the books.csv file
    reader = csv.reader(f) #read the data
    next(reader, None) #Skip the first row

    #insert data into books table
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books(isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {"isbn":isbn, "title":title, "author":author, "year": year})
    db.commit()
    print("Done importing all the information regarding to books from the books.csv to the database.")

if __name__ == "__main__":
    main()
