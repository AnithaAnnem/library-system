# app.py
from flask import Flask, request, jsonify
from models import add_book, get_all_books, borrow_book, return_book

app = Flask(__name__)

@app.route("/books", methods=["GET"])
def list_books():
    return jsonify(get_all_books())

@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    add_book(
        title=data["title"],
        author=data["author"],
        isbn=data["isbn"],
        total_copies=data["total_copies"]
    )
    return jsonify({"message": "Book added successfully"}), 201

@app.route("/books/borrow", methods=["POST"])
def borrow():
    data = request.get_json()
    result = borrow_book(data["title"])
    if result is True:
        return jsonify({"message": "Book borrowed"})
    elif result is False:
        return jsonify({"message": "No copies available"}), 400
    return jsonify({"message": "Book not found"}), 404

@app.route("/books/return", methods=["POST"])
def return_book_api():
    data = request.get_json()
    result = return_book(data["title"])
    if result:
        return jsonify({"message": "Book returned"})
    return jsonify({"message": "Book not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
