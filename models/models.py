from collections import UserDict
import datetime


class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = self._validate(new_value)

    def _validate(self, value):
        return value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def _validate(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class Phone(Field):
    def _validate(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValueError(f"Phone number must be 10 digits, got: '{value}'")
        return value

    def __eq__(self, other):
        if isinstance(other, Phone):
            return self.value == other.value
        return NotImplemented

    def __hash__(self):
        return hash(self.value)


class Birthday(Field):
    DATE_FORMAT = "%d.%m.%Y"

    def _validate(self, value):
        try:
            birthday = datetime.datetime.strptime(value, Birthday.DATE_FORMAT).date()
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid birthday format '{value}'. Expected DD.MM.YYYY (e.g. 25.03.1990)."
            )
        if birthday > datetime.date.today():
            raise ValueError(f"Birthday cannot be in the future: '{value}'.")
        return birthday

    def __str__(self):
        return self._value.strftime(Birthday.DATE_FORMAT)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = set()
        self.birthday = None

    def add_phone(self, phone):
        if self.find_phone(phone):
            raise ValueError(f"Phone {phone} already exists for this contact.")
        self.phones.add(Phone(phone))

    def set_phone(self, phone):
        self.phones.clear()
        self.add_phone(phone)

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj is None:
            raise ValueError(f"Phone {phone} not found in record")
        self.phones.discard(phone_obj)

    def edit_phone(self, old_phone, new_phone):
        """Replace old_phone with new_phone. Returns True if new_phone already
        existed (phones merged), False if it was a regular update."""
        phone_obj = self.find_phone(old_phone)
        if phone_obj is None:
            raise ValueError(f"Phone {old_phone} not found in record")
        merged = self.find_phone(new_phone) is not None
        self.phones.discard(phone_obj)
        if not merged:
            self.phones.add(Phone(new_phone))
        return merged

    def find_phone(self, phone):
        return next((p for p in self.phones if p.value == phone), None)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(sorted(p.value for p in self.phones)) or "—"
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday is None:
                continue
            birthday = record.birthday.value
            birthday_this_year = self._birthday_in_year(birthday, today.year)

            if birthday_this_year < today:
                birthday_this_year = self._birthday_in_year(birthday, today.year + 1)

            days_until = (birthday_this_year - today).days
            if 0 <= days_until <= 6:
                birthday_str = birthday.strftime(Birthday.DATE_FORMAT)
                weekday = birthday_this_year.weekday()
                if weekday == 5:
                    birthday_this_year += datetime.timedelta(days=2)
                elif weekday == 6:
                    birthday_this_year += datetime.timedelta(days=1)
                upcoming.append(
                    {
                        "name": record.name.value,
                        "birthday": birthday_str,
                        "congratulation_date": birthday_this_year.strftime(
                            Birthday.DATE_FORMAT
                        ),
                    }
                )
        return upcoming

    @staticmethod
    def _birthday_in_year(birthday: datetime.date, year: int) -> datetime.date:
        """Return birthday adjusted to the given year. Feb 29 → Mar 1 in non-leap years."""
        try:
            return birthday.replace(year=year)
        except ValueError:
            return datetime.date(year, 3, 1)

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
