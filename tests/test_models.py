import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import add_book, get_all_books, borrow_book, return_book, books


import pytest
from models import add_book, get_all_books, borrow_book, return_book, books

@pytest.fixture
def reset_books():
    books.clear()
    yield
    books.clear()

def test_add_book(reset_books):
    add_book("Python Basics", "Guido", "123", 3)
    assert len(get_all_books()) == 1

def test_borrow_book(reset_books):
    add_book("Python", "Author", "123", 2)
    result = borrow_book("Python")
    assert result is True
    assert get_all_books()[0]["available_copies"] == 1

def test_return_book(reset_books):
    add_book("Python", "Author", "123", 1)
    borrow_book("Python")
    return_book("Python")
    assert get_all_books()[0]["available_copies"] == 1
