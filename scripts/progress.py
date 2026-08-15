#!/usr/bin/env python3

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROGRESS_FILE = BASE_DIR / "challenges" / "progress.json"


def load_progress():

    with open(
        PROGRESS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def progress_bar(completed, total, width=20):

    if total == 0:
        return "[" + "-" * width + "]"

    percentage = completed / total

    filled = int(
        percentage * width
    )

    return (
        "["
        + "#" * filled
        + "-" * (width - filled)
        + "]"
    )


def main():

    progress = load_progress()

    print()
    print("======================================")
    print("       🚀 DEVELOPER LEARNING LAB")
    print("======================================")
    print()

    print(
        f"Current Level: "
        f"{progress['level_name']}"
    )

    print(
        f"Challenges Completed: "
        f"{progress['total_challenges_completed']}"
    )

    print()
    print("Technology Progress")
    print("-------------------")

    for technology, data in progress[
        "technologies"
    ].items():

        completed = data["completed"]
        total = data["total"]

        percentage = (
            int(completed / total * 100)
            if total > 0
            else 0
        )

        bar = progress_bar(
            completed,
            total
        )

        print(
            f"{technology:<12} "
            f"{bar} "
            f"{percentage}%"
        )

    print()


if __name__ == "__main__":
    main()
