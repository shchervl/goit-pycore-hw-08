"""Unit tests for models/models.py — Name, Phone, Birthday, Record, AddressBook."""

import datetime

import pytest

from models.models import Name, Phone, Birthday, Record, AddressBook
from tests.helpers import birthday_n_days_from_now, days_until_next


# ─── Name ─────────────────────────────────────────────────────────────────────

class TestName:
    def test_valid_name_stores_value(self):
        assert Name("Alice").value == "Alice"

    def test_str_returns_value(self):
        assert str(Name("Bob")) == "Bob"

    # Negative
    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty"):
            Name("")

    def test_reassign_to_empty_raises(self):
        n = Name("Alice")
        with pytest.raises(ValueError):
            n.value = ""


# ─── Phone ────────────────────────────────────────────────────────────────────

class TestPhone:
    # Positive
    def test_valid_10_digit_phone(self):
        assert Phone("1234567890").value == "1234567890"

    def test_str_returns_digits(self):
        assert str(Phone("0987654321")) == "0987654321"

    def test_equal_phones_are_equal(self):
        assert Phone("1234567890") == Phone("1234567890")

    def test_different_phones_are_not_equal(self):
        assert Phone("1234567890") != Phone("0987654321")

    def test_equal_phones_have_same_hash(self):
        assert hash(Phone("1234567890")) == hash(Phone("1234567890"))

    def test_set_deduplicates_equal_phones(self):
        assert len({Phone("1234567890"), Phone("1234567890")}) == 1

    # Boundary values
    def test_9_digits_raises(self):           # one below minimum
        with pytest.raises(ValueError):
            Phone("123456789")

    def test_10_digits_is_valid(self):        # exact minimum/maximum
        Phone("1234567890")                   # must not raise

    def test_11_digits_raises(self):          # one above maximum
        with pytest.raises(ValueError):
            Phone("12345678901")

    # Negative
    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            Phone("")

    def test_dashes_raise(self):
        with pytest.raises(ValueError):
            Phone("123-456-789")

    def test_spaces_raise(self):
        with pytest.raises(ValueError):
            Phone("123 456 789")

    def test_letters_raise(self):
        with pytest.raises(ValueError):
            Phone("123456789a")

    # Setter path
    def test_setter_rejects_invalid_value(self):
        p = Phone("1234567890")
        with pytest.raises(ValueError):
            p.value = "123"

    def test_setter_accepts_valid_value(self):
        p = Phone("1234567890")
        p.value = "0987654321"
        assert p.value == "0987654321"


# ─── Birthday ─────────────────────────────────────────────────────────────────

class TestBirthday:
    # Positive
    def test_valid_past_date(self):
        assert str(Birthday("01.01.1990")) == "01.01.1990"

    def test_str_round_trip(self):
        assert str(Birthday("25.12.1985")) == "25.12.1985"

    # Boundary: today is the latest valid birthday
    def test_today_is_valid(self):
        today_str = datetime.date.today().strftime("%d.%m.%Y")
        assert str(Birthday(today_str)) == today_str

    # Boundary: yesterday is valid
    def test_yesterday_is_valid(self):
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        Birthday(yesterday)  # must not raise

    # Boundary: tomorrow is the first invalid date
    def test_tomorrow_raises(self):
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        with pytest.raises(ValueError, match="future"):
            Birthday(tomorrow)

    # Negative
    def test_iso_format_raises(self):
        with pytest.raises(ValueError, match="DD.MM.YYYY"):
            Birthday("1990-01-01")

    def test_invalid_day_raises(self):
        with pytest.raises(ValueError):
            Birthday("32.01.1990")

    def test_invalid_month_raises(self):
        with pytest.raises(ValueError):
            Birthday("01.13.1990")

    def test_non_date_string_raises(self):
        with pytest.raises(ValueError):
            Birthday("not-a-date")

    # Setter path
    def test_setter_rejects_invalid_format(self):
        b = Birthday("01.01.1990")
        with pytest.raises(ValueError, match="DD.MM.YYYY"):
            b.value = "1990-01-01"

    def test_setter_rejects_future_date(self):
        b = Birthday("01.01.1990")
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        with pytest.raises(ValueError, match="future"):
            b.value = tomorrow

    def test_setter_accepts_valid_date(self):
        b = Birthday("01.01.1990")
        b.value = "15.06.1985"
        assert str(b) == "15.06.1985"


# ─── Record ───────────────────────────────────────────────────────────────────

class TestRecord:
    # Positive
    def test_new_record_has_no_phones_or_birthday(self):
        r = Record("Alice")
        assert r.name.value == "Alice"
        assert len(r.phones) == 0
        assert r.birthday is None

    def test_add_phone_is_findable(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        assert r.find_phone("1234567890") is not None

    def test_find_returns_correct_phone(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        assert r.find_phone("1234567890").value == "1234567890"

    def test_find_nonexistent_phone_returns_none(self):
        assert Record("Alice").find_phone("0000000000") is None

    def test_remove_phone_makes_it_unfindable(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.remove_phone("1234567890")
        assert r.find_phone("1234567890") is None

    def test_edit_phone_replaces_old_with_new(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        merged = r.edit_phone("1234567890", "0987654321")
        assert merged is False
        assert r.find_phone("1234567890") is None
        assert r.find_phone("0987654321") is not None

    def test_edit_phone_to_existing_merges_and_returns_true(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.add_phone("0987654321")
        merged = r.edit_phone("1234567890", "0987654321")
        assert merged is True
        assert r.find_phone("1234567890") is None
        assert len(r.phones) == 1

    def test_add_birthday_stores_formatted_string(self):
        r = Record("Alice")
        r.add_birthday("01.01.1990")
        assert str(r.birthday) == "01.01.1990"

    def test_str_contains_name_phone_and_birthday(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        r.add_birthday("01.01.1990")
        s = str(r)
        assert "Alice" in s
        assert "1234567890" in s
        assert "01.01.1990" in s

    def test_str_without_phones_shows_dash(self):
        assert "—" in str(Record("Alice"))

    # Negative
    def test_add_duplicate_phone_raises(self):
        r = Record("Alice")
        r.add_phone("1234567890")
        with pytest.raises(ValueError, match="already exists"):
            r.add_phone("1234567890")

    def test_remove_nonexistent_phone_raises(self):
        with pytest.raises(ValueError, match="not found"):
            Record("Alice").remove_phone("1234567890")

    def test_edit_nonexistent_old_phone_raises(self):
        with pytest.raises(ValueError, match="not found"):
            Record("Alice").edit_phone("0000000000", "1111111111")


# ─── AddressBook ──────────────────────────────────────────────────────────────

class TestAddressBook:
    def test_add_and_find_record(self):
        book = AddressBook()
        r = Record("Alice")
        book.add_record(r)
        assert book.find("Alice") is r

    def test_find_nonexistent_returns_none(self):
        assert AddressBook().find("Nobody") is None

    def test_delete_removes_record(self):
        book = AddressBook()
        book.add_record(Record("Alice"))
        book.delete("Alice")
        assert book.find("Alice") is None

    def test_delete_nonexistent_is_noop(self):
        AddressBook().delete("Nobody")  # must not raise

    def test_str_contains_record_info(self):
        book = AddressBook()
        r = Record("Alice")
        r.add_phone("1234567890")
        book.add_record(r)
        assert "Alice" in str(book)


# ─── AddressBook._birthday_in_year ────────────────────────────────────────────

class TestBirthdayInYear:
    """Direct unit tests of the static helper — no mocking needed."""

    def test_regular_date_replaces_year(self):
        d = datetime.date(1990, 6, 15)
        assert AddressBook._birthday_in_year(d, 2024) == datetime.date(2024, 6, 15)

    def test_feb29_in_non_leap_year_becomes_mar1(self):
        feb29 = datetime.date(1992, 2, 29)
        result = AddressBook._birthday_in_year(feb29, 2023)  # 2023 is not a leap year
        assert result == datetime.date(2023, 3, 1)

    def test_feb29_in_leap_year_stays_feb29(self):
        feb29 = datetime.date(1992, 2, 29)
        result = AddressBook._birthday_in_year(feb29, 2024)  # 2024 is a leap year
        assert result == datetime.date(2024, 2, 29)


# ─── AddressBook.get_upcoming_birthdays ───────────────────────────────────────

class TestGetUpcomingBirthdays:
    """All birthdays are computed relative to the real today() — no mocking.

    birthday_n_days_from_now(n) creates a date whose anniversary is exactly n days
    from today, using year 1990 (or 1992 for Feb 29) so Birthday._validate passes.
    Window rule: [today, today+6] inclusive.  Sat/Sun → congratulate on Monday.
    """

    def _book(self, name: str, birthday_str: str) -> AddressBook:
        book = AddressBook()
        r = Record(name)
        r.add_birthday(birthday_str)
        book.add_record(r)
        return book

    # Boundary: 0 days (today) — included
    def test_birthday_today_is_included(self):
        book = self._book("Alice", birthday_n_days_from_now(0))
        assert any(u["name"] == "Alice" for u in book.get_upcoming_birthdays())

    # Boundary: 1 day away — included
    def test_birthday_tomorrow_is_included(self):
        book = self._book("Alice", birthday_n_days_from_now(1))
        assert any(u["name"] == "Alice" for u in book.get_upcoming_birthdays())

    # Boundary: 6 days — last day still inside the window
    def test_birthday_6_days_away_is_included(self):
        book = self._book("Alice", birthday_n_days_from_now(6))
        assert any(u["name"] == "Alice" for u in book.get_upcoming_birthdays())

    # Boundary: 7 days — first day outside the window
    def test_birthday_7_days_away_is_excluded(self):
        book = self._book("Alice", birthday_n_days_from_now(7))
        assert not any(u["name"] == "Alice" for u in book.get_upcoming_birthdays())

    # Boundary: yesterday — anniversary rolls to next year (~364 days), excluded
    def test_birthday_yesterday_is_excluded(self):
        book = self._book("Alice", birthday_n_days_from_now(-1))
        assert not any(u["name"] == "Alice" for u in book.get_upcoming_birthdays())

    def test_saturday_birthday_congratulation_on_monday(self):
        offset = days_until_next(5)  # days until next Saturday (always 0–6)
        book = self._book("Alice", birthday_n_days_from_now(offset))
        alice = next(u for u in book.get_upcoming_birthdays() if u["name"] == "Alice")
        congrat = datetime.datetime.strptime(alice["congratulation_date"], "%d.%m.%Y").date()
        assert congrat.weekday() == 0  # Monday

    def test_sunday_birthday_congratulation_on_monday(self):
        offset = days_until_next(6)  # days until next Sunday (always 0–6)
        book = self._book("Alice", birthday_n_days_from_now(offset))
        alice = next(u for u in book.get_upcoming_birthdays() if u["name"] == "Alice")
        congrat = datetime.datetime.strptime(alice["congratulation_date"], "%d.%m.%Y").date()
        assert congrat.weekday() == 0  # Monday

    def test_weekday_birthday_congratulation_on_same_day(self):
        # Find any weekday (Mon–Fri) within the window
        for offset in range(7):
            wd = (datetime.date.today() + datetime.timedelta(days=offset)).weekday()
            if wd < 5:  # Mon–Fri
                break
        book = self._book("Alice", birthday_n_days_from_now(offset))
        alice = next(u for u in book.get_upcoming_birthdays() if u["name"] == "Alice")
        congrat = datetime.datetime.strptime(alice["congratulation_date"], "%d.%m.%Y").date()
        assert congrat.weekday() == wd

    def test_result_contains_required_keys(self):
        book = self._book("Alice", birthday_n_days_from_now(0))
        entry = next(u for u in book.get_upcoming_birthdays() if u["name"] == "Alice")
        assert {"name", "birthday", "congratulation_date"} <= entry.keys()

    def test_contact_without_birthday_is_excluded(self):
        book = AddressBook()
        book.add_record(Record("NoBirthday"))
        assert book.get_upcoming_birthdays() == []

    def test_empty_book_returns_empty_list(self):
        assert AddressBook().get_upcoming_birthdays() == []

    def test_only_in_window_contacts_are_returned(self):
        book = AddressBook()
        inside = Record("Inside")
        inside.add_birthday(birthday_n_days_from_now(0))
        book.add_record(inside)
        outside = Record("Outside")
        outside.add_birthday(birthday_n_days_from_now(7))
        book.add_record(outside)
        names = [u["name"] for u in book.get_upcoming_birthdays()]
        assert "Inside" in names
        assert "Outside" not in names
