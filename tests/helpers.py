"""Shared test utilities — plain functions, not pytest fixtures."""

import datetime


def birthday_n_days_from_now(n: int) -> str:
    """Return a birthday string (DD.MM.YYYY) whose anniversary falls exactly n
    days from today.  Uses 1990 as birth year (1992 for Feb 29 in leap years)
    so the date is always in the past and passes Birthday._validate.
    Negative n is allowed — yesterday's anniversary rolls to next year in the bot.
    """
    target = datetime.date.today() + datetime.timedelta(days=n)
    year = 1992 if (target.month == 2 and target.day == 29) else 1990
    return datetime.date(year, target.month, target.day).strftime("%d.%m.%Y")


def days_until_next(weekday: int) -> int:
    """Return offset (0–6) until the next occurrence of *weekday* (0=Mon … 6=Sun).
    A 7-day window always contains every weekday exactly once, so this never fails.
    """
    today = datetime.date.today()
    for d in range(7):
        if (today + datetime.timedelta(days=d)).weekday() == weekday:
            return d
    raise RuntimeError("unreachable")
