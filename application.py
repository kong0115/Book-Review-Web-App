import os
import requests

from utils import *
from flask import Flask, render_template, request, session, url_for, jsonify
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

# key for the goodreads API
api_key = "eXUp7Y0RGO1i9NNO8c0Q"

# login is required to access default route
@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    """
    If it is a GET request, just render the home page.

    If it is a POST request, search for matching books, authors, and titles in the database,
    then render the search results to the user.
    """

    username = session.get('username')
    session["books"] = []
    if request.method == "GET":
        return render_template("index.html", username = username)
    else:
        keyword = str(request.form.get("search"))
        search = '%' + keyword + '%'
        searchResults = db.execute("SELECT * FROM books WHERE isbn ILIKE :search OR title ILIKE :search OR author ILIKE :search", {"search":search}).fetchall()
        if len(searchResults) == 0:
            search_message = 'Sorry. Nothing match "' + keyword + '".'
        else:
            for result in searchResults:
                session["books"].append(result)
                search_message = 'Found: ' + str(len(searchResults)) + ' matches.'
        return render_template("search_results.html", search_message = search_message, books = session["books"], username = username)

#route for user to log in
@app.route("/login")
def login():

    """
    Render a page to ask user to provide username and password to log in.
    """

    login_message = ""
    return render_template("login.html", login_message = login_message)

#route for login authentication
@app.route("/login/authenticate", methods=["POST"])
def login_authenticate():

    """
    Check if the login credentials (username and password) is in the database.
    It it is not in the database, return error message and ask user to try a new credentials.
    Otherwise, the user has successfully logged in, and redirect the user to home page.
    """

    username = request.form.get("username")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username":username, "password":password}).rowcount == 0:
        login_message = "Wrong username or password. Please try again."
        return render_template("login.html", login_message =login_message)
    else:
        session["username"] = username
        return redirect(url_for('index'))

#route for user to sign up
@app.route("/signup")
def signup():

    """
    Render a page to ask user to provide information required to sign up for the application.
    """

    signup_message = ""
    return render_template("signup.html", signup_message = signup_message)

#route for validating the information provided by the user from the sign up page
@app.route("/signup/authenticate", methods=["POST"])
def signup_authenticate():

    """
    If at least one of the fields on the sign up page is missing,
    return error message and prompt the user to fill the sign up form again.
    We also check if the username already exists. If it is a new username,
    insert the user information into the users table in the database and redirect user to the login page.
    Otherwise, return error message and prompt the user to fill the sign up form again.
    """

    username = request.form.get("username")
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    password = request.form.get("password")
    if username=="" or fullname=="" or email =="" or password =="":
        signup_message = "Some fields are missing. Please fill in all the fields and try again."
        return render_template("signup.html", signup_message = signup_message)
    if db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).rowcount == 0:
        db.execute("INSERT INTO users (username, fullname, email, password) VALUES (:username, :fullname, :email, :password)",
            {"username":username, "fullname":fullname, "email":email, "password":password})
        db.commit()
        signup_message = "Sign up successfully. Please log in now."
        return render_template("login.html", login_message = signup_message)
    else:
        signup_message = "Username already exists. Please try a new username."
        return render_template("signup.html", signup_message = signup_message)

#route to get the information of the book with matching isbn
@app.route("/isbn/<string:isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):

    """
    If it is a GET request, check if there is any book with matching isbn in the database.
    Return error message if book with specified isbn not found.

    If it is a POST request, get the user review data(rating and comment).
    If the user has already submitted a review for the book, return error message to indicate multiple reviews are not allowed.
    If the user review is missing rating, comment, or both, return error message.
    Otherwise, insert the user review data into the database.

    For both GET and POST request, get the review data from goodreads api, reviews and book details from our database.
    Return a book page that consists of 4 sections: book details, goodreads review data, our website reviews, and review submission.
    """

    username = session.get('username')
    session["reviews"] = []
    error_message = ""
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    if book is None:
        error_message = "ISBN not found."
        return render_template("search_results.html", search_message = error_message, username = username)
    if request.method =="POST":
        if db.execute("SELECT * FROM reviews WHERE user_id = :username AND book_id = :isbn", {"username":username,"isbn":isbn}).rowcount == 0:
            star = request.form.get('rate');
            review = request.form.get('comment')
            if star is not None and review != "":
                db.execute("INSERT INTO reviews(book_id, user_id, rating, text) VALUES (:isbn, :username, :star, :review)",  {"isbn":isbn, "username":username, "star":star, "review":review})
                db.commit()
            elif star is not None and review == "":
                error_message = "No review is given. Please try again."
            elif star is None and review != "":
                error_message = "No rating is given. Please try again."
            else:
                error_message = "Missing both rating and review. Please try again."
        else:
            error_message = "Multiple reviews for the same book is not allowed."

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn})
    data = res.json()
    reviews_count = data["books"][0]["work_ratings_count"]
    average_rating = data["books"][0]["average_rating"]
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :isbn", {"isbn":isbn}).fetchall()
    for review in reviews:
        session["reviews"].append(review)

    return render_template("book.html", username = username, book = book, count = reviews_count, rating = average_rating, reviews = session["reviews"], error_message = error_message)

#route to render a json object that consists of details of the book with specified isbn
@app.route("/api/isbn/<string:isbn>")
def api(isbn):

    """
    Check if the book with requested isbn is in the database.
    Return a 404 error if the book is not found.
    Otherwise, get the reviews count and average rating from goodreads api,
    and return an json object that contains the book’s title, author, publication year,
    isbn, reviews count, and average rating.
    """
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    if book is None:
        return render_template('error.html'),404
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn})
    data = res.json()
    reviews_count = data["books"][0]["work_ratings_count"]
    average_rating = data["books"][0]["average_rating"]
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": reviews_count,
        "average_score": average_rating
    })

#logout route
@app.route("/logout")
def logout():

    """
    Clear the user session and redirect user to the login page.
    """

    session.clear()
    return redirect(url_for("login"))
