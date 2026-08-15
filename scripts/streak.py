#!/usr/bin/env python3

import json
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

COMPLETIONS_FILE = (
    BASE_DIR
    / "challenges"
    / "completions.json"
)


def load_completions():
    """Load challenge completion history."""

    if not COMPLETIONS_FILE.exists():
        return []

    with open(
        COMPLETIONS_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_learning_dates(completions):
    """Return unique completion dates."""

    dates = set()

    for completion in completions:

        try:
            completion_date = date.fromisoformat(
                completion["date"]
            )

            dates.add(completion_date)

        except (KeyError, ValueError):
            continue

    return dates


def calculate_current_streak(learning_dates):
    """Calculate the current consecutive learning streak."""

    if not learning_dates:
        return 0

    today = date.today()

    # If the user hasn't learned today,
    # allow yesterday to be the latest active day.

    if today in learning_dates:

        current_day = today

    elif today - timedelta(days=1) in learning_dates:

        current_day = today - timedelta(days=1)

    else:

        return 0

    streak = 0

    while current_day in learning_dates:

        streak += 1

        current_day -= timedelta(days=1)

    return streak


def calculate_longest_streak(learning_dates):
    """Calculate the longest consecutive learning streak."""

    if not learning_dates:
        return 0

    sorted_dates = sorted(learning_dates)

    longest = 1
    current = 1

    for index in range(1, len(sorted_dates)):

        previous_day = sorted_dates[index - 1]
        current_day = sorted_dates[index]

        if current_day == previous_day + timedelta(days=1):

            current += 1

            longest = max(
                longest,
                current
            )

        else:

            current = 1

    return longest


def main():

    completions = load_completions()

    learning_dates = get_learning_dates(
        completions
    )

    current_streak = calculate_current_streak(
        learning_dates
    )

    longest_streak = calculate_longest_streak(
        learning_dates
    )

    print()
    print("🔥 Learning Streak")
    print("------------------")

    print(
        f"Current streak: {current_streak} days"
    )

    print(
        f"Longest streak: {longest_streak} days"
    )

    print(
        f"Learning days: {len(learning_dates)}"
    )

    print()


if __name__ == "__main__":
    main()
