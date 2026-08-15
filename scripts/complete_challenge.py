#!/usr/bin/env python3

import argparse
import json
import re
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

CHALLENGES_FILE = BASE_DIR / "challenges" / "challenges.json"
PROGRESS_FILE = BASE_DIR / "challenges" / "progress.json"
DAILY_DIR = BASE_DIR / "daily"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def find_challenge(challenges, challenge_id):
    for technology, challenge_list in challenges.items():
        for challenge in challenge_list:
            if challenge["id"] == challenge_id:
                return technology, challenge

    return None, None


def main():

    parser = argparse.ArgumentParser(
        description="Complete the daily developer challenge."
    )

    parser.add_argument(
        "--date",
        dest="challenge_date",
        help="Complete a challenge for a specific date (YYYY-MM-DD)."
    )

    args = parser.parse_args()

    if args.challenge_date:

        try:
            challenge_day = date.fromisoformat(
                args.challenge_date
            )

        except ValueError:

            print(
                "Invalid date. Use YYYY-MM-DD."
            )

            return

    else:

        challenge_day = date.today()

    today = challenge_day.isoformat()

    daily_file = DAILY_DIR / f"{today}.md"

    if not daily_file.exists():
        print(f"No daily challenge found for {today}.")
        return

    challenges = load_json(CHALLENGES_FILE)
    progress = load_json(PROGRESS_FILE)

    daily_content = daily_file.read_text(
        encoding="utf-8"
    )

    challenge_id = None

    # Read today's Challenge ID directly from
    # the daily Markdown file.

    match = re.search(
        r"\*\*Challenge ID:\*\*\s*([A-Za-z0-9_-]+)",
        daily_content
    )

    if match:
        challenge_id = match.group(1)

    if not challenge_id:

        print(
            "Could not identify today's challenge ID."
        )

        print(
            "Make sure today's daily file contains:"
        )

        print(
            "**Challenge ID:** challenge-id"
        )

        return

    if not challenge_id:

        print(
            "Could not identify today's challenge ID."
        )

        print(
            "Make sure today's daily file contains:"
        )

        print(
            "**Challenge ID:** challenge-id"
        )

        return

    technology, challenge = find_challenge(
        challenges,
        challenge_id
    )

    if not challenge:
        print(
            f"Challenge not found: {challenge_id}"
        )
        return

    completed = progress["completed_challenges"]

    if challenge_id in completed:

        print(
            f"Challenge already completed: "
            f"{challenge_id}"
        )

        return

    # Record completion.

    completed.append(challenge_id)

    progress["total_challenges_completed"] += 1

    if technology in progress["technologies"]:

        progress["technologies"][technology]["completed"] += 1

    save_json(
        PROGRESS_FILE,
        progress
    )

    print()
    print("✅ Challenge completed!")
    print()
    print(f"Challenge: {challenge['title']}")
    print(f"Technology: {technology}")
    print(f"Date: {today}")
    print(f"Challenge ID: {challenge_id}")
    print()
    print(
        "Total challenges completed:",
        progress["total_challenges_completed"]
    )


if __name__ == "__main__":
    main()
