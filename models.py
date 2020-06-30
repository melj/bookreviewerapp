from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = "users"	
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)

class Book(db.Model):
	__tablename__ = "books"	
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String, nullable=False)
	author = db.Column(db.String, nullable=False)
	year = db.Column(db.String, nullable=False)
	isbn = db.Column(db.String, nullable=False)

class Review(db.Model):
	__tablename__ = "reviews"	
	id = db.Column(db.Integer, primary_key=True)
	rating = db.Column(db.Integer, nullable=False)
	content = db.Column(db.String, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
