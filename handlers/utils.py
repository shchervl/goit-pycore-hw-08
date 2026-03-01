from colorama import Style

from config import BOT_ERROR_COLOR, IDENT
from models.errors import UsageError


def require_args(args, count: int, message: str):
    """Raise UsageError if fewer than `count` arguments were provided."""
    if len(args) < count:
        raise UsageError(message)


def get_record_or_raise(book, name: str, not_found_msg: str = None):
    username = name.capitalize()
    record = book.find(username)
    if record is None:
        raise KeyError(not_found_msg or f"Contact '{username}' doesn't exist.")
    return username, record
