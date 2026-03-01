from colorama import Style
from tabulate import tabulate
from models.commands import command
from config import (
    IDENT, BOT_COLOR, BOT_ERROR_COLOR,
    ERR_NAME_AND_BIRTHDAY, ERR_NAME_ONLY,
)
from handlers.utils import get_record_or_raise, require_args


@command("add-birthday", usage="add-birthday <name> <DD.MM.YYYY> – add a birthday to a contact.")
def add_birthday(args, book):
    require_args(args, 2, ERR_NAME_AND_BIRTHDAY)
    name, birthday_str = args
    username, record = get_record_or_raise(
        book, name,
        not_found_msg=f"Contact '{name.capitalize()}' not found. Add the contact first.",
    )
    record.add_birthday(birthday_str)
    return f"{IDENT}{BOT_COLOR}Birthday added.{Style.RESET_ALL}"


@command("show-birthday", usage="show-birthday <name> – show a contact's birthday.")
def show_birthday(args, book):
    require_args(args, 1, ERR_NAME_ONLY)
    username, record = get_record_or_raise(book, args[0])
    if record.birthday is None:
        return f"{IDENT}{BOT_COLOR}{username} has no birthday set.{Style.RESET_ALL}"
    return f"{IDENT}{BOT_COLOR}{username}'s birthday is {record.birthday}.{Style.RESET_ALL}"


@command("birthdays", usage="birthdays – show contacts with birthdays in the next week.")
def birthdays_cmd(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return f"{IDENT}{BOT_ERROR_COLOR}No birthdays in the next week.{Style.RESET_ALL}"
    data = [(u["name"], u["birthday"], u["congratulation_date"]) for u in upcoming]
    return BOT_COLOR + tabulate(
        data,
        headers=["Name", "Birthday", "Congratulate on"],
        tablefmt="rounded_grid",
    ) + Style.RESET_ALL
