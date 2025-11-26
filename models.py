# In-memory storage
books = []

# Add a new book
def add_book(title, author, isbn, total_copies):
    book = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "total_copies": total_copies,
        "available_copies": total_copies
    }
    books.append(book)

# Get all books
def get_all_books():
    return books

# Borrow book
def borrow_book(title):
    for book in books:
        if book["title"].lower() == title.lower():
            if book["available_copies"] > 0:
                book["available_copies"] -= 1
                return True
            else:
                return False
    return None

# Return book
def return_book(title):
    for book in books:
        if book["title"].lower() == title.lower():
            book["available_copies"] += 1
            return True
    return None
