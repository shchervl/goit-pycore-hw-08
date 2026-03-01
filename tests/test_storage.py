"""Tests for storage/storage.py — load_book and save_book."""

import pytest

from models.models import AddressBook, Record
from storage.storage import load_book, save_book


class TestLoadBook:
    def test_returns_fresh_book_when_no_file(self, tmp_path):
        path = tmp_path / "book.pkl"
        book = load_book(path)
        assert isinstance(book, AddressBook)
        assert len(book.data) == 0

    def test_returns_saved_book(self, tmp_path):
        path = tmp_path / "book.pkl"
        original = AddressBook()
        r = Record("Alice")
        r.add_phone("1234567890")
        original.add_record(r)
        save_book(original, path)

        loaded = load_book(path)
        assert "Alice" in loaded.data
        assert loaded.find("Alice").find_phone("1234567890") is not None

    def test_corrupt_file_returns_fresh_book(self, tmp_path):
        path = tmp_path / "book.pkl"
        path.write_bytes(b"not valid pickle data")

        book = load_book(path)
        assert isinstance(book, AddressBook)
        assert len(book.data) == 0

    def test_corrupt_file_creates_bak(self, tmp_path):
        path = tmp_path / "book.pkl"
        path.write_bytes(b"not valid pickle data")

        load_book(path)
        assert path.with_suffix(".bak").exists()
        assert not path.exists()

    def test_corrupt_file_prints_warning(self, tmp_path, capsys):
        path = tmp_path / "book.pkl"
        path.write_bytes(b"not valid pickle data")

        load_book(path)
        assert "Warning" in capsys.readouterr().out


class TestSaveBook:
    def test_round_trip(self, tmp_path):
        path = tmp_path / "book.pkl"
        book = AddressBook()
        r = Record("Bob")
        r.add_phone("0987654321")
        book.add_record(r)

        save_book(book, path)
        loaded = load_book(path)
        assert "Bob" in loaded.data

    def test_creates_file(self, tmp_path):
        path = tmp_path / "book.pkl"
        save_book(AddressBook(), path)

        assert path.exists()
