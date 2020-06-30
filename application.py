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

@app.route("/")
def login():
	return render_template("login.html")

@app.route("/index", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		name = request.form.get('username')
		pword = request.form.get('password')
		user = db.execute("SELECT * FROM users WHERE username=:name", {"name": name}).fetchone()

		if user is None or user.password != pword:
			return render_template("error.html", message="Access denied. Wrong credentials.")
		else:
			session['curr_user'] = name;

	books = db.execute("SELECT * FROM books").fetchall()
	
	if books is None:
		return render_template("error.html", "Could not get books. Please try again")
	return render_template("index.html", books=books)

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
	if request.method == "POST":
		if 'curr_user' not in session:
			return render_template("error.html", message='Please Login or Sign up to review this book')			
		else:
			user_id = session['curr_user'].id						
			content = request.form.get("review")
			rating = request.form.get("rating")
			db.execute("INSERT INTO reviews (rating, content, user_id, book_id) VALUES (:rating, :content, :user_id, :book_id)",
                    {"rating": rating, "content": content, "user_id": user_id, "book_id": book.id})
			db.commit()

	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
	if book is None:
		return render_template("error.html", message="No book was found for this ISBN code")

	reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
	session['curr_book'] = book	
	return render_template("book.html", book=book, reviews=reviews)

@app.route("/logout")
def logout():
	session.pop('curr_user')
	return redirect(url_for("login"))


