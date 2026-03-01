from colorama import Style
from tabulate import tabulate
from models.commands import command, registry
from config import IDENT, BOT_COLOR


@command("hello")
def hello_cmd(args, book):
    return f"{IDENT}{BOT_COLOR}How can I help you?{Style.RESET_ALL}"


@command("help")
def help_cmd(args, book):
    rows = [(c.name, c.usage) for c in registry.values() if c.usage]
    if rows:
        return BOT_COLOR + tabulate(rows, headers=["Command", "Usage"], tablefmt="rounded_grid") + Style.RESET_ALL
