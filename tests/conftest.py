"""Pytest fixtures shared across all test modules."""

import pytest

from models.models import AddressBook, Record


@pytest.fixture
def book():
    return AddressBook()


@pytest.fixture
def alice_record():
    r = Record("Alice")
    r.add_phone("1234567890")
    return r


@pytest.fixture
def book_with_alice(book, alice_record):
    book.add_record(alice_record)
    return book
