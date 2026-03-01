"""
Contact Management Bot

A command-line bot for managing contacts with phone numbers and birthdays.
"""

import handlers  # noqa: F401 — imported to registers all @command handlers
import readline  # noqa: F401 — enables arrow keys and history in input()
from colorama import Style
from models.commands import registry
from config import IDENT, BOT_COLOR, BOT_ERROR_COLOR
from models.models import AddressBook


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.strip().lower(), args


def main():
    book = AddressBook()
    print(f"{BOT_COLOR}Welcome to the assistant bot!{Style.RESET_ALL}")

    try:
        while True:
            user_input = input("Enter a command: ").strip()
            cmd, args = parse_input(user_input)

            if cmd in ["close", "exit"]:
                print(f"{BOT_COLOR}Good bye!{Style.RESET_ALL}")
                break
            elif cmd in registry:
                result = registry[cmd](args, book)
                if result:
                    print(result)
            elif cmd:
                print(
                    f"{IDENT}{BOT_ERROR_COLOR}Invalid command. Type 'help' to see available commands.{Style.RESET_ALL}"
                )
    except KeyboardInterrupt:
        print(f"\n{BOT_COLOR}Good bye!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
