from colorama import Style
from tabulate import tabulate
from models.commands import command
from config import (
    IDENT, BOT_COLOR, BOT_ERROR_COLOR,
    ERR_NAME_AND_PHONE, ERR_NAME_AND_PHONES, ERR_NAME_ONLY,
)
from handlers.utils import get_record_or_raise, require_args
from models.models import Record


@command("add", usage="add <name> <phone> - add a contact with phone or add phone to the contact.")
def add_contact(args, book):
    require_args(args, 2, ERR_NAME_AND_PHONE)
    name, phone = args
    username = name.capitalize()
    record = book.find(username)
    if record is None:
        record = Record(username)
        record.add_phone(phone)
        book.add_record(record)
        return f"{IDENT}{BOT_COLOR}Contact added.{Style.RESET_ALL}"
    record.add_phone(phone)
    return f"{IDENT}{BOT_COLOR}Phone added to existing contact.{Style.RESET_ALL}"


@command("change", usage="change <name> <old phone> <new phone> - change a contact's phone.")
def update_contact(args, book):
    require_args(args, 3, ERR_NAME_AND_PHONES)
    name, old_phone, new_phone = args
    username, record = get_record_or_raise(book, name)
    merged = record.edit_phone(old_phone, new_phone)
    if merged:
        return f"{IDENT}{BOT_COLOR}{new_phone} already exists — {old_phone} removed.{Style.RESET_ALL}"
    return f"{IDENT}{BOT_COLOR}Contact updated.{Style.RESET_ALL}"


@command("phone", usage="phone <name> - get the phone of a contact.")
def get_users_phone(args, book):
    require_args(args, 1, ERR_NAME_ONLY)
    username, record = get_record_or_raise(book, args[0])
    return BOT_COLOR + tabulate(
        [(username, "\n".join(p.value for p in record.phones))],
        headers=["Name", "Phone(s)"],
        tablefmt="rounded_grid",
    ) + Style.RESET_ALL


@command("all", usage="all - list all contacts.")
def all_contacts(args, book):
    if not book.data:
        return f"{IDENT}{BOT_ERROR_COLOR}No contacts yet.{Style.RESET_ALL}"
    data = [
        (
            r.name.value,
            "\n".join(p.value for p in r.phones) or "—",
            str(r.birthday) if r.birthday else "—",
        )
        for r in book.data.values()
    ]
    return BOT_COLOR + tabulate(
        data,
        headers=["Name", "Phone(s)", "Birthday"],
        tablefmt="rounded_grid",
    ) + Style.RESET_ALL
