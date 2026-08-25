#!/usr/bin/env python3

import argparse
import json
import random
from datetime import date
from pathlib import Path


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CHALLENGES_FILE = BASE_DIR / "challenges" / "challenges.json"
ROADMAP_FILE = BASE_DIR / "challenges" / "roadmap.json"
PROGRESS_FILE = BASE_DIR / "challenges" / "progress.json"

DAILY_DIR = BASE_DIR / "daily"
HISTORY_FILE = DAILY_DIR / ".challenge_history.json"


# --------------------------------------------------
# Load JSON files
# --------------------------------------------------

def load_json(file_path):
    """Load a JSON file."""

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# Challenge history
# --------------------------------------------------

def load_history():
    """Load previously used challenge IDs."""

    if not HISTORY_FILE.exists():
        return []

    return load_json(HISTORY_FILE)


def save_history(history):
    """Save used challenge IDs."""

    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


# --------------------------------------------------
# Select technology from roadmap
# --------------------------------------------------

def get_today_technology(roadmap, challenge_day):
    """Determine the technology for the requested date."""

    day_name = challenge_day.strftime("%A").lower()

    rotation = roadmap["weekly_rotation"]

    return rotation.get(day_name)
# --------------------------------------------------
# Select challenge
# --------------------------------------------------

def choose_challenge(
    challenges,
    technology,
    history,
    completed_ids
):

    if technology == "project" or challenge is None:

        print("Today's focus is a project/review day.")

        return None

    if technology not in challenges:

        print(
            f"No challenges found for technology: {technology}"
        )

        return None

    available = []

    for challenge in challenges[technology]:

        challenge_id = challenge["id"]

        if (
            challenge_id not in history
            and challenge_id not in completed_ids
        ):

            available.append(challenge)

    # If all challenges for this technology were used,
    # reset only that technology's challenges.

    if not available:

        print(
            f"All {technology} challenges have been used."
        )

        print(
            f"Resetting {technology} challenge history."
        )

        technology_ids = {
            challenge["id"]
            for challenge in challenges[technology]
        }

        history[:] = [challenge_id
            for challenge_id in history
            if challenge_id not in technology_ids]

        available = [
            challenge
	    for challenge in challenges[technology]
	    if challenge["id"] not in completed_ids
        ]

    if not available:

        print(
            f"🎉 All {technology} challenges are completed!"
        )

        return None

    return random.choice(available)

# --------------------------------------------------
# Create daily challenge
# --------------------------------------------------

def create_daily_file(
    technology,
    challenge,
    history,
    challenge_day
):
    """Create today's Markdown learning challenge."""

    today = challenge_day.isoformat()

    DAILY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = DAILY_DIR / f"{today}.md"

    # Prevent overwriting today's challenge.

    if output_file.exists():

        print(
            f"Daily challenge already exists: {output_file}"
        )

        return

    # --------------------------------------------------
    # Project / review day
    # --------------------------------------------------

    if technology == "project":

        content = f"""# 🚀 Daily Developer Project Day

**Date:** {today}

## 🎯 Focus

Project / Review

## 📚 Today's Goal

Review the technologies and concepts learned during the week.

## ✅ Suggested Activities

1. Review this week's challenges.
2. Choose one challenge and improve your solution.
3. Refactor code where possible.
4. Add documentation.
5. Commit your work to Git.
6. Review what you learned this week.

## ⭐ Bonus

Create a small project that combines at least two technologies learned this week.

## 📈 Learning Goal

Turn individual exercises into practical development experience.

---

*Generated automatically by Developer Learning Lab.*
"""

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(content)

        print(
            f"Created project/review day: {output_file}"
        )

        return

    # --------------------------------------------------
    # Normal challenge
    # --------------------------------------------------

    content = f"""# 🚀 Daily Developer Challenge

**Date:** {today}
**Challenge ID:** {challenge["id"]}

## 🎯 Focus

{technology.title()}

## 🧩 Challenge

### {challenge["title"]}

**Difficulty:** {challenge["difficulty"]}

{challenge["objective"]}

## 📚 Concepts

"""

    for concept in challenge["concepts"]:

        content += f"- {concept}\n"

    content += "\n## ✅ Tasks\n\n"

    for number, task in enumerate(
        challenge["task"],
        start=1
    ):

        content += f"{number}. {task}\n"

    content += f"""
## ⭐ Bonus Challenge

{challenge["bonus"]}

## 🛠️ Technology

**{technology.title()}**

## 📈 Learning Goal

Practice the concepts above by implementing the challenge yourself.

---

*Generated automatically by Developer Learning Lab.*
"""

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    # Record the challenge.

    history.append(challenge["id"])

    save_history(history)

    print(
        f"Created daily challenge: {output_file}"
    )


# --------------------------------------------------
# Main program
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Generate the daily developer challenge."
    )

    parser.add_argument(
        "--date",
        dest="challenge_date",
        help="Generate a challenge for a specific date (YYYY-MM-DD)."
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

    #today = challenge_day.isoformat()



    print("🚀 Developer Learning Lab")
    print("-------------------------")

    challenges = load_json(
        CHALLENGES_FILE
    )

    roadmap = load_json(
        ROADMAP_FILE
    )

    history = load_history()

    progress = load_json(
	 PROGRESS_FILE
    )

    completed_ids = set(
	 progress["completed_challenges"]
    )

    technology = get_today_technology(
        roadmap,
	challenge_day
    )

    print(
        f"Today's technology: {technology}"
    )

    challenge = choose_challenge(
        challenges,
        technology,
        history,
        completed_ids
    )

    create_daily_file(
        technology,
        challenge,
        history,
	challenge_day
    )


# --------------------------------------------------
# Program entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()
