from Logger import app, db, bcrypt
from Logger.models import Users, Books
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
import string
import secrets
import requests


@app.route('/')
def home():
    return render_template('index.html')


def generate_key() -> str:
    """generates api key for registering user : time complexity 0(n)"""
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(32))
    print(f'api key : {api_key}')
    if Users().check_existing_key(api_key):
        generate_key()
    else:
        return api_key


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        new_user = Users(
            username=request.form["username"],
            password=bcrypt.generate_password_hash(request.form["password"], rounds=10),
            email=request.form["email"],
            api_key=generate_key()
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = Users.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    # query all books from current_users's the db
    books = Books.query.filter_by(owner_id=current_user.id).all()
    # sending the length of books to make the serial number ordered rather than using primary_key
    number_of_books = len(books)
    return render_template('dashboard.html', current_user=current_user, books=books, number_of_books=number_of_books)


@app.route('/logout')
@login_required
def logout():
    # logout the user
    logout_user()
    session.clear()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
    # add new book form site to db
    if request.method == "POST":
        new_book = Books(
            book_title=request.form['bookname'],
            book_author=request.form['authorname'],
            book_rating=request.form['bookrating'],
            owner_id=current_user.id
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(f'dashboard')
    return render_template('add.html')


@app.route('/edit/<int:book_id>', methods=["GET", "POST"])
@login_required
def edit(book_id):
    # query selected book to edit
    book_to_edit = Books.query.filter_by(book_id=book_id).first()
    if request.method == 'POST':
        book_to_edit.book_name = request.form['bookname']
        book_to_edit.book_author = request.form['authorname']
        book_to_edit.book_rating = request.form['bookrating']
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit.html', current_book=book_to_edit)


@app.route('/remove/<int:book_id>')
@login_required
def remove(book_id):
    # delete a specific book
    book_to_delete = Books.query.filter_by(book_id=book_id).first()
    print(book_to_delete)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))


# REST - API
@app.route('/BL-api/get all')
def get_all_books():
    """response : all books stored by the user.
    params{api_key : users_api_key}"""
    api_key = request.args.get('api_key')
    # querying requested user from UserTable using api key
    owner = Users.query.filter_by(api_key=api_key).first()
    if owner:
        books = Books.query.filter_by(owner_id=owner.id).all()
        return jsonify(response=[book.to_dict() for book in books]), 200
    return jsonify(error='Check your API key & try again.'), 404


GOOGLE_BOOKS_API_KEY = 'YOUR_GOOGLE_BOOKS_API_KEY'


def get_data(isbn) -> dict:
    """returns Google books API data"""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'isbn:{isbn}',
        'key': GOOGLE_BOOKS_API_KEY,
        'printType': 'books'
    }
    response = requests.get(url=base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    return {}


@app.route('/BL-api/get info/')
def get_book_info():
    """response : info about requested book by its ISBN 10 from Google Books API.
    params{api_key : users_api_key, isbn: ISBN-10 number of the book}"""
    api_key = request.args.get('api_key')
    owner = Users.query.filter_by(api_key=api_key).first()
    if owner:
        book_data = get_data(request.args.get('isbn'))
        if book_data:
            return jsonify(response=book_data), 200
    return jsonify(error='Check your API key & try again.'), 404


@app.route('/BL-api/add new book', methods=['POST'])
def add_new_book():
    """response: add new book to db.
    params{api_key : users_api_key, book_title: book name, book_author: book author, book_rating: your rating}"""
    api_key = request.args.get('api_key')
    owner = Users.query.filter_by(api_key=api_key).first()
    if owner:
        book_title = request.args.get('book_title')
        new_book = Books(
            book_title=book_title,
            book_author=request.args.get('book_author'),
            book_rating=request.args.get('book_rating'),
            owner_id=owner.id
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify(response={'Success': f"Added {book_title} to {owner.username}'s table"}), 200
    return jsonify(error='Check your API key & try again.'), 404


@app.route('/BL-api/edit book', methods=['PATCH'])
def edit_book():
    """response: edits an existing book.
    params{api_key : users_api_key, book_id: book_id of updating book, new_rating: current book rating}"""
    api_key = request.args.get('api_key')
    requested_book_id = request.args.get('book_id')
    owner = Users.query.filter_by(api_key=api_key).first()
    book_to_edit = Books.query.filter_by(book_id=requested_book_id).first()
    if owner and book_to_edit:
        new_rating = request.args.get('new_rating')
        book_to_edit.book_rating = new_rating
        db.session.commit()
        return jsonify(response={"Success": f"Updated {book_to_edit.book_title} book rating to {new_rating}."}), 200
    return jsonify(error="Check your API key or book ID & try again."), 404


@app.route('/BL-api/delete book', methods=["DELETE"])
def delete_book():
    """response: deletes an existing book.
    params{api_key : users_api_key, book_id: book_id of deleting book}"""
    api_key = request.args.get('api_key')
    requested_book_id = request.args.get('book_id')
    owner = Users.query.filter_by(api_key=api_key).first()
    book_to_delete = Books.query.filter_by(book_id=requested_book_id).first()
    if owner and book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()
        return jsonify(response={"Success": f"Book {book_to_delete.book_title} deleted successfully."}), 200
    return jsonify(error="Check your API key or book ID & try again."), 404
