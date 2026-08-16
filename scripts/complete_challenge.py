#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CHALLENGES_FILE = BASE_DIR / "challenges" / "challenges.json"
PROGRESS_FILE = BASE_DIR / "challenges" / "progress.json"
COMPLETIONS_FILE = BASE_DIR / "challenges" / "completions.json"
EVIDENCE_FILE = BASE_DIR / "evidence" / "evidence.json"
DAILY_DIR = BASE_DIR / "daily"


# --------------------------------------------------
# JSON helpers
# --------------------------------------------------

def load_json(file_path):
    """Load a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    """Save data as formatted JSON."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


# --------------------------------------------------
# Challenge lookup
# --------------------------------------------------

def find_challenge(challenges, challenge_id):
    """Find a challenge by its ID."""

    for technology, challenge_list in challenges.items():
        for challenge in challenge_list:
            if challenge["id"] == challenge_id:
                return technology, challenge

    return None, None


# --------------------------------------------------
# Main program
# --------------------------------------------------

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

    # --------------------------------------------------
    # Determine challenge date
    # --------------------------------------------------

    if args.challenge_date:

        try:
            challenge_day = date.fromisoformat(
                args.challenge_date
            )

        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")
            return

    else:
        challenge_day = date.today()

    today = challenge_day.isoformat()

    # --------------------------------------------------
    # Find daily challenge
    # --------------------------------------------------

    daily_file = DAILY_DIR / f"{today}.md"

    if not daily_file.exists():
        print(
            f"No daily challenge found for {today}."
        )
        return

    # --------------------------------------------------
    # Load project data
    # --------------------------------------------------

    challenges = load_json(
        CHALLENGES_FILE
    )

    progress = load_json(
        PROGRESS_FILE
    )

    if COMPLETIONS_FILE.exists():
        completions = load_json(
            COMPLETIONS_FILE
        )
    else:
        completions = []

    # --------------------------------------------------
    # Load learning evidence
    # --------------------------------------------------

    if EVIDENCE_FILE.exists():
        evidence = load_json(
            EVIDENCE_FILE
        )
    else:
        evidence = []

    # --------------------------------------------------
    # Read daily challenge
    # --------------------------------------------------

    daily_content = daily_file.read_text(
        encoding="utf-8"
    )

    challenge_id = None

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

    # --------------------------------------------------
    # Find challenge
    # --------------------------------------------------

    technology, challenge = find_challenge(
        challenges,
        challenge_id
    )

    if not challenge:
        print(
            f"Challenge not found: {challenge_id}"
        )
        return

    # --------------------------------------------------
    # Check if already completed
    # --------------------------------------------------

    completed = progress[
        "completed_challenges"
    ]

    if challenge_id in completed:
        print(
            f"Challenge already completed: "
            f"{challenge_id}"
        )
        return

    # --------------------------------------------------
    # Record completion in progress
    # --------------------------------------------------

    completed.append(
        challenge_id
    )

    progress[
        "total_challenges_completed"
    ] += 1

    if technology in progress["technologies"]:

        progress["technologies"][
            technology
        ]["completed"] += 1

    # --------------------------------------------------
    # Record completion history
    # --------------------------------------------------

    completion_record = {
        "challenge_id": challenge_id,
        "technology": technology,
        "date": today
    }

    completions.append(
        completion_record
    )

    # --------------------------------------------------
    # Record learning evidence
    # --------------------------------------------------

    evidence_record = {
        "challenge_id": challenge_id,
        "technology": technology,
        "date": today,
        "title": challenge["title"],
        "difficulty": challenge["difficulty"],
        "status": "completed",
        "objective": challenge["objective"],
        "concepts": challenge["concepts"]
    }

    evidence.append(
        evidence_record
    )

    # --------------------------------------------------
    # Save progress
    # --------------------------------------------------

    save_json(
        PROGRESS_FILE,
        progress
    )

    # --------------------------------------------------
    # Save completion history
    # --------------------------------------------------

    save_json(
        COMPLETIONS_FILE,
        completions
    )

    # --------------------------------------------------
    # Save learning evidence
    # --------------------------------------------------

    save_json(
        EVIDENCE_FILE,
        evidence
    )

    print(
        "📝 Learning evidence recorded."
    )

    # --------------------------------------------------
    # Update dashboard automatically
    # --------------------------------------------------

    dashboard_script = (
        BASE_DIR
        / "scripts"
        / "dashboard.py"
    )

    try:

        subprocess.run(
            [
                "python3",
                str(dashboard_script)
            ],
            check=True
        )

        print(
            "📊 Dashboard updated successfully."
        )

    except subprocess.CalledProcessError:

        print(
            "⚠️ Challenge completed, "
            "but dashboard update failed."
        )

    # --------------------------------------------------
    # Display result
    # --------------------------------------------------

    print()
    print("✅ Challenge completed!")
    print()

    print(
        f"Challenge: {challenge['title']}"
    )

    print(
        f"Technology: {technology}"
    )

    print(
        f"Date: {today}"
    )

    print(
        f"Challenge ID: {challenge_id}"
    )

    print()

    print(
        "Total challenges completed:",
        progress[
            "total_challenges_completed"
        ]
    )

# --------------------------------------------------
# Git automation
# --------------------------------------------------

git_automation_script = (
    BASE_DIR
    / "scripts"
    / "git_automation.py"
)

git_commit_message = (
    f"feat: complete {challenge_id} challenge"
)

try:

    subprocess.run(
        [
            "python3",
            str(git_automation_script),
            git_commit_message
        ],
        check=True
    )

except subprocess.CalledProcessError:

    print()
    print(
        "⚠️ Challenge completed, "
        "but Git automation failed."
    )

# --------------------------------------------------
# Program entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()

