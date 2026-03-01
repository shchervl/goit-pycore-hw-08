"""Tests for handlers/birthdays.py — add-birthday, show-birthday, birthdays commands."""

import datetime

import pytest

import handlers  # noqa: F401 — registers all @command decorators before _COMMANDS is used
from handlers.birthdays import add_birthday, show_birthday, birthdays_cmd
from models.commands import registry
from models.errors import UsageError
from models.models import AddressBook, Record
from tests.helpers import birthday_n_days_from_now, days_until_next


# ─── add_birthday ─────────────────────────────────────────────────────────────

class TestAddBirthday:
    # Positive
    def test_valid_past_birthday_returns_success(self, book_with_alice):
        result = add_birthday(["Alice", "01.01.1990"], book_with_alice)
        assert "Birthday added" in result

    def test_valid_past_birthday_is_stored_in_record(self, book_with_alice):
        add_birthday(["Alice", "01.01.1990"], book_with_alice)
        assert str(book_with_alice.find("Alice").birthday) == "01.01.1990"

    # Boundary: today is the latest valid birthday
    def test_today_as_birthday_is_accepted(self, book_with_alice):
        today_str = datetime.date.today().strftime("%d.%m.%Y")
        result = add_birthday(["Alice", today_str], book_with_alice)
        assert "Birthday added" in result

    def test_today_as_birthday_is_stored_in_record(self, book_with_alice):
        today_str = datetime.date.today().strftime("%d.%m.%Y")
        add_birthday(["Alice", today_str], book_with_alice)
        assert str(book_with_alice.find("Alice").birthday) == today_str

    # Boundary: tomorrow is the first invalid birthday
    def test_tomorrow_as_birthday_raises(self, book_with_alice):
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        with pytest.raises(ValueError, match="future"):
            add_birthday(["Alice", tomorrow], book_with_alice)

    # Negative
    def test_unknown_contact_raises_key_error(self, book):
        with pytest.raises(KeyError):
            add_birthday(["Nobody", "01.01.1990"], book)

    def test_wrong_date_format_raises(self, book_with_alice):
        with pytest.raises(ValueError, match="DD.MM.YYYY"):
            add_birthday(["Alice", "1990-01-01"], book_with_alice)

    def test_zero_args_raises_usage_error(self, book):
        with pytest.raises(UsageError):
            add_birthday([], book)

    def test_one_arg_raises_usage_error(self, book_with_alice):
        with pytest.raises(UsageError):
            add_birthday(["Alice"], book_with_alice)

    # Update path — contact already has a birthday
    def test_overwriting_existing_birthday_returns_success(self, book_with_alice):
        add_birthday(["Alice", "01.01.1990"], book_with_alice)
        result = add_birthday(["Alice", "15.06.1985"], book_with_alice)
        assert "Birthday added" in result

    def test_overwriting_birthday_updates_record(self, book_with_alice):
        add_birthday(["Alice", "01.01.1990"], book_with_alice)
        add_birthday(["Alice", "15.06.1985"], book_with_alice)
        assert str(book_with_alice.find("Alice").birthday) == "15.06.1985"


# ─── show_birthday ────────────────────────────────────────────────────────────

class TestShowBirthday:
    # Positive
    def test_returns_birthday_string(self, book_with_alice):
        book_with_alice.find("Alice").add_birthday("15.06.1990")
        result = show_birthday(["alice"], book_with_alice)
        assert "Alice" in result
        assert "birthday is" in result
        assert "15.06.1990" in result

    def test_contact_without_birthday_says_so(self, book_with_alice):
        result = show_birthday(["alice"], book_with_alice)
        assert "Alice" in result
        assert "no birthday set" in result

    # Boundary: minimum required args = 1
    def test_zero_args_raises_usage_error(self, book):
        with pytest.raises(UsageError):
            show_birthday([], book)

    # Negative
    def test_unknown_contact_raises_key_error(self, book):
        with pytest.raises(KeyError):
            show_birthday(["nobody"], book)


# ─── birthdays_cmd ────────────────────────────────────────────────────────────

class TestBirthdaysCmd:
    """Uses birthday_n_days_from_now() so dates are always relative to real today
    — no mocking needed.
    """

    # Positive
    def test_contact_with_birthday_today_is_shown(self, book):
        bday = birthday_n_days_from_now(0)
        r = Record("Alice")
        r.add_birthday(bday)
        book.add_record(r)
        result = birthdays_cmd([], book)
        assert "Alice" in result
        assert bday in result                          # birthday column
        today = datetime.date.today()
        wd = today.weekday()
        if wd == 5:                                    # Saturday → Monday
            expected_congrat = today + datetime.timedelta(days=2)
        elif wd == 6:                                  # Sunday → Monday
            expected_congrat = today + datetime.timedelta(days=1)
        else:
            expected_congrat = today
        assert expected_congrat.strftime("%d.%m.%Y") in result

    def test_contact_with_birthday_in_6_days_is_shown(self, book):
        r = Record("Alice")
        r.add_birthday(birthday_n_days_from_now(6))
        book.add_record(r)
        assert "Alice" in birthdays_cmd([], book)

    def test_saturday_birthday_shows_monday_as_congratulation(self, book):
        offset = days_until_next(5)
        r = Record("Alice")
        r.add_birthday(birthday_n_days_from_now(offset))
        book.add_record(r)
        result = birthdays_cmd([], book)
        monday = (datetime.date.today() + datetime.timedelta(days=offset + (7 - 5))).strftime(
            "%d.%m.%Y"
        )
        assert monday in result

    def test_sunday_birthday_shows_monday_as_congratulation(self, book):
        offset = days_until_next(6)
        r = Record("Alice")
        r.add_birthday(birthday_n_days_from_now(offset))
        book.add_record(r)
        result = birthdays_cmd([], book)
        monday = (datetime.date.today() + datetime.timedelta(days=offset + (7 - 6))).strftime(
            "%d.%m.%Y"
        )
        assert monday in result

    # Boundary: empty book
    def test_empty_book_returns_no_birthdays_message(self, book):
        assert "No birthdays" in birthdays_cmd([], book)

    # Boundary: birthday outside 7-day window
    def test_birthday_in_7_days_not_shown(self, book):
        r = Record("Alice")
        r.add_birthday(birthday_n_days_from_now(7))
        book.add_record(r)
        assert "Alice" not in birthdays_cmd([], book)

    # Negative: contact with no birthday set
    def test_contact_without_birthday_not_shown(self, book):
        book.add_record(Record("NoBirthday"))
        assert "No birthdays" in birthdays_cmd([], book)


# ─── Error messages returned by the Command wrapper ───────────────────────────
# Calls via registry["name"](args, book) — tests what the user actually sees.

class TestBirthdayCommandErrorMessages:
    def test_add_birthday_no_args_returns_usage_message(self, book):
        result = registry["add-birthday"]([], book)
        assert "Give me name and birthday please." in result

    def test_add_birthday_no_args_includes_usage_hint(self, book):
        result = registry["add-birthday"]([], book)
        assert "add-birthday" in result  # usage hint appended for UsageError

    def test_add_birthday_unknown_contact_returns_not_found_message(self, book):
        result = registry["add-birthday"](["Nobody", "01.01.1990"], book)
        assert "not found" in result
        assert "Add the contact first" in result

    def test_add_birthday_invalid_format_returns_format_hint(self, book_with_alice):
        result = registry["add-birthday"](["Alice", "1990-01-01"], book_with_alice)
        assert "DD.MM.YYYY" in result

    def test_add_birthday_future_date_returns_future_message(self, book_with_alice):
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        result = registry["add-birthday"](["Alice", tomorrow], book_with_alice)
        assert "future" in result

    def test_show_birthday_no_args_returns_usage_message(self, book):
        result = registry["show-birthday"]([], book)
        assert "Give me a name please." in result

    def test_show_birthday_no_args_includes_usage_hint(self, book):
        result = registry["show-birthday"]([], book)
        assert "show-birthday" in result  # usage hint appended for UsageError

    def test_show_birthday_unknown_contact_returns_not_found_message(self, book):
        result = registry["show-birthday"](["nobody"], book)
        assert "doesn't exist" in result
