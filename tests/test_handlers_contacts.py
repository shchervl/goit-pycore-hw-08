"""Tests for handlers/contacts.py — add, change, phone, all commands."""

import pytest

import handlers  # noqa: F401 — registers all @command decorators before _COMMANDS is used
from handlers.contacts import add_contact, update_contact, get_users_phone, all_contacts
from models.commands import registry
from models.errors import UsageError
from models.models import Record


# ─── add_contact ──────────────────────────────────────────────────────────────

class TestAddContact:
    # Positive
    def test_new_contact_returns_added_message(self, book):
        result = add_contact(["alice", "1234567890"], book)
        assert "Contact added" in result

    def test_new_contact_is_stored_in_book(self, book):
        add_contact(["alice", "1234567890"], book)
        assert book.find("Alice") is not None

    def test_new_contact_phone_is_stored_in_record(self, book):
        add_contact(["alice", "1234567890"], book)
        assert book.find("Alice").find_phone("1234567890") is not None

    def test_name_is_capitalized(self, book):
        add_contact(["alice", "1234567890"], book)
        assert book.find("Alice") is not None

    def test_phone_added_to_existing_contact(self, book_with_alice):
        result = add_contact(["alice", "0987654321"], book_with_alice)
        assert "Phone added" in result

    def test_second_phone_is_stored(self, book_with_alice):
        add_contact(["alice", "0987654321"], book_with_alice)
        assert book_with_alice.find("Alice").find_phone("0987654321") is not None

    # Boundary: minimum required args = 2
    def test_zero_args_raises_usage_error(self, book):
        with pytest.raises(UsageError):
            add_contact([], book)

    def test_one_arg_raises_usage_error(self, book):
        with pytest.raises(UsageError):
            add_contact(["alice"], book)

    # Negative
    def test_invalid_phone_format_raises(self, book):
        with pytest.raises(ValueError):
            add_contact(["alice", "123"], book)

    def test_duplicate_phone_raises(self, book_with_alice):
        with pytest.raises(ValueError, match="already exists"):
            add_contact(["alice", "1234567890"], book_with_alice)


# ─── update_contact ───────────────────────────────────────────────────────────

class TestUpdateContact:
    # Positive
    def test_change_phone_returns_success_message(self, book_with_alice):
        result = update_contact(["alice", "1234567890", "0987654321"], book_with_alice)
        assert "Contact updated" in result

    def test_old_phone_is_removed_after_change(self, book_with_alice):
        update_contact(["alice", "1234567890", "0987654321"], book_with_alice)
        assert book_with_alice.find("Alice").find_phone("1234567890") is None

    def test_new_phone_is_stored_after_change(self, book_with_alice):
        update_contact(["alice", "1234567890", "0987654321"], book_with_alice)
        assert book_with_alice.find("Alice").find_phone("0987654321") is not None

    def test_change_to_existing_phone_reports_merge(self, book_with_alice):
        book_with_alice.find("Alice").add_phone("0987654321")
        result = update_contact(["alice", "1234567890", "0987654321"], book_with_alice)
        assert "0987654321 already exists" in result
        assert "1234567890 removed" in result

    def test_merge_leaves_only_target_phone_in_record(self, book_with_alice):
        book_with_alice.find("Alice").add_phone("0987654321")
        update_contact(["alice", "1234567890", "0987654321"], book_with_alice)
        record = book_with_alice.find("Alice")
        assert len(record.phones) == 1
        assert record.find_phone("0987654321") is not None
        assert record.find_phone("1234567890") is None

    # Boundary: minimum required args = 3
    def test_two_args_raises_usage_error(self, book_with_alice):
        with pytest.raises(UsageError):
            update_contact(["alice", "1234567890"], book_with_alice)

    def test_zero_args_raises_usage_error(self, book):
        with pytest.raises(UsageError):
            update_contact([], book)

    # Negative
    def test_unknown_contact_raises_key_error(self, book):
        with pytest.raises(KeyError):
            update_contact(["nobody", "1234567890", "0987654321"], book)

    def test_old_phone_not_found_raises_value_error(self, book_with_alice):
        with pytest.raises(ValueError, match="not found"):
            update_contact(["alice", "0000000000", "1111111111"], book_with_alice)


# ─── get_users_phone ──────────────────────────────────────────────────────────

class TestGetUsersPhone:
    # Positive
    def test_returns_name_and_phone(self, book_with_alice):
        result = get_users_phone(["alice"], book_with_alice)
        assert "Alice" in result
        assert "1234567890" in result

    def test_multiple_phones_all_appear(self, book_with_alice):
        book_with_alice.find("Alice").add_phone("0987654321")
        result = get_users_phone(["alice"], book_with_alice)
        assert "1234567890" in result
        assert "0987654321" in result

    # Boundary: minimum required args = 1
    def test_zero_args_raises_usage_error(self, book):
        with pytest.raises(UsageError):
            get_users_phone([], book)

    # Negative
    def test_unknown_contact_raises_key_error(self, book):
        with pytest.raises(KeyError):
            get_users_phone(["nobody"], book)


# ─── all_contacts ─────────────────────────────────────────────────────────────

class TestAllContacts:
    # Boundary: empty book
    def test_empty_book_returns_no_contacts_message(self, book):
        result = all_contacts([], book)
        assert "No contacts" in result

    # Positive
    def test_returns_contact_name(self, book_with_alice):
        assert "Alice" in all_contacts([], book_with_alice)

    def test_returns_phone_number(self, book_with_alice):
        assert "1234567890" in all_contacts([], book_with_alice)

    def test_birthday_shown_when_set(self, book_with_alice):
        book_with_alice.find("Alice").add_birthday("01.01.1990")
        assert "01.01.1990" in all_contacts([], book_with_alice)

    def test_multiple_contacts_all_listed(self, book_with_alice):
        bob = Record("Bob")
        bob.add_phone("5555555555")
        book_with_alice.add_record(bob)
        result = all_contacts([], book_with_alice)
        assert "Alice" in result
        assert "Bob" in result


# ─── Error messages returned by the Command wrapper ───────────────────────────
# Calls via registry["name"](args, book) — tests what the user actually sees.

class TestContactCommandErrorMessages:
    def test_add_no_args_returns_usage_message(self, book):
        result = registry["add"]([], book)
        assert "Give me name and phone please." in result

    def test_add_no_args_includes_usage_hint(self, book):
        result = registry["add"]([], book)
        assert "add <name> <phone>" in result  # usage hint appended for UsageError

    def test_add_invalid_phone_returns_digit_count_message(self, book):
        result = registry["add"](["alice", "123"], book)
        assert "10 digits" in result

    def test_add_duplicate_phone_returns_exists_message(self, book_with_alice):
        result = registry["add"](["alice", "1234567890"], book_with_alice)
        assert "already exists" in result

    def test_change_no_args_returns_usage_message(self, book):
        result = registry["change"]([], book)
        assert "Give me name, old phone and new phone please." in result

    def test_change_no_args_includes_usage_hint(self, book):
        result = registry["change"]([], book)
        assert "change <name>" in result  # usage hint appended for UsageError

    def test_change_unknown_contact_returns_not_found_message(self, book):
        result = registry["change"](["nobody", "1234567890", "0987654321"], book)
        assert "doesn't exist" in result

    def test_change_old_phone_not_found_returns_not_found_message(self, book_with_alice):
        result = registry["change"](["alice", "0000000000", "1111111111"], book_with_alice)
        assert "not found" in result

    def test_phone_no_args_returns_usage_message(self, book):
        result = registry["phone"]([], book)
        assert "Give me a name please." in result

    def test_phone_no_args_includes_usage_hint(self, book):
        result = registry["phone"]([], book)
        assert "phone <name>" in result  # usage hint appended for UsageError

    def test_phone_unknown_contact_returns_not_found_message(self, book):
        result = registry["phone"](["nobody"], book)
        assert "doesn't exist" in result
