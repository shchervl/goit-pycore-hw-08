from colorama import Style
from tabulate import tabulate
from models.commands import command, registry
from config import IDENT, BOT_COLOR, STORAGE_PATH
from storage.storage import save_book


@command("hello")
def hello_cmd(args, book):
    return f"{IDENT}{BOT_COLOR}How can I help you?{Style.RESET_ALL}"


@command("help")
def help_cmd(args, book):
    rows = [(c.name, c.usage) for c in registry.values() if c.usage]
    if rows:
        return BOT_COLOR + tabulate(rows, headers=["Command", "Usage"], tablefmt="rounded_grid") + Style.RESET_ALL


@command("save", usage="save")
def save_cmd(args, book):
    save_book(book, STORAGE_PATH)
    return f"{IDENT}{BOT_COLOR}Contacts saved.{Style.RESET_ALL}"
