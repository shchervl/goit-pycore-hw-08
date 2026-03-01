import pickle
from pathlib import Path

from models.models import AddressBook


def load_book(path: Path) -> AddressBook:
    if not path.exists():
        return AddressBook()
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        bak = path.with_suffix(".bak")
        path.rename(bak)
        print(
            f"Warning: could not load '{path}' ({e}). Starting fresh. Backup saved to '{bak}'."
        )
        return AddressBook()


def save_book(book: AddressBook, path: Path) -> None:
    try:
        with open(path, "wb") as f:
            pickle.dump(book, f)
    except OSError as e:
        print(f"Warning: could not save contacts ({e}). Your changes were not persisted.")
