import os

from flask import Flask, session, render_template, request, redirect, url_for
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


# Log in a user Route
@app.route("/", methods=["GET", "POST"])
def login():
	# GET request, just render template
	if request.method == "GET":
		return render_template("login.html")

	# POST request, get form data
	name = request.form.get('username')
	pword = request.form.get('password')

	# validate empty fields, render error if so
	if len(name) < 1 or len(pword) < 1:
		return render_template("login.html", error="Access denied. Fill in the fields.")

	# retrieve user from database
	user = db.execute("SELECT * FROM users WHERE username=:name", {"name": name}).fetchone()

	# validate user exists and password, render error if so
	if user is None or user.password != pword:
		return render_template("login.html", error="Access denied. Wrong credentials.")
	
	# All good, update session and redirect to index page
	session['curr_user'] = user.username
	return redirect(url_for("index"))

# Get the sign up page, Or Create a new user Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
	# GET request, just render template
	if request.method == "GET":
		return render_template("signup.html")

	# POST request, get form data
	name = request.form.get('username')
	password = request.form.get('password')
	confirm_password = request.form.get('confirm-password')

	# validate empty fields, render error if so
	if len(name) < 1 or len(password) < 1:
		return render_template("signup.html", error="Ensure all fields are filled out.")

	# validate password fields, render error if so
	if password != confirm_password:
		return render_template("signup.html", error="Password's don't match.")

	# validate user does not already exist
	user = db.execute("SELECT * FROM users WHERE username=:name", {"name": name}).fetchone()

	if user is None:
		# create a user and log them in
		db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username": name, "password": password })
		db.commit()
		session['curr_user'] = name
		return redirect(url_for("index"))
	else:
		# the user name already exists, load page with error message
		return render_template("signup.html", error="The username '" + name +  "'' already exists")

# Main page displays all the books
@app.route("/index", methods=["GET", "POST"])
def index():
	# Retrieve 10 books from the db
	books = db.execute("SELECT * FROM books LIMIT 10").fetchall()

	if 'curr_user' not in session:
		user = None
	else:
		user = session['curr_user']

	return render_template("index.html", books=books, user=user)

# Get a specific book's details and reviews
# User can also create a review here
@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
	if book is None:
		return render_template("book.html", error="No book was found for this ISBN code")

	if request.method == "POST":
		if 'curr_user' not in session:
			return render_template("login.html", error='Please Login or Sign up to review this book', user=None)

		content = request.form.get("review")
		rating = request.form.get("rating")
		db.execute("INSERT INTO reviews (rating, content, user_id, book_id) VALUES (:rating, :content, :user_id, :book_id)",
                {"rating": rating, "content": content, "user_id": session['curr_user'], "book_id": book.id})
		db.commit()

	reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
	session['curr_book'] = book	

	if 'curr_user' not in session:
		user = None
	else:
		user = session['curr_user']

	return render_template("book.html", book=book, reviews=reviews, user=user)

# Sign the user out Route
@app.route("/logout")
def logout():
	# Pop the user from our session and go back to login
	session.pop('curr_user')
	return redirect(url_for("login"))

