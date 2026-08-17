#!/usr/bin/env python3

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


FILES = {
    "challenges": BASE_DIR / "challenges" / "challenges.json",
    "progress": BASE_DIR / "challenges" / "progress.json",
    "completions": BASE_DIR / "challenges" / "completions.json",
    "evidence": BASE_DIR / "evidence" / "evidence.json",
}


def load_json(name, path):
    print(f"Checking {name}...")

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print()
    print("======================================")
    print("     🔍 PROJECT VALIDATION")
    print("======================================")
    print()

    data = {}

    for name, path in FILES.items():

        if not path.exists():
            raise FileNotFoundError(
                f"Missing file: {path}"
            )

        data[name] = load_json(
            name,
            path
        )

    if not data["challenges"]:
        raise ValueError(
            "challenges.json is empty."
        )

    challenge_ids = {
        challenge["id"]
        for challenges in data["challenges"].values()
        for challenge in challenges
    }

    completed_ids = set(
        data["progress"]["completed_challenges"]
    )

    unknown_completed = (
        completed_ids - challenge_ids
    )

    if unknown_completed:
        raise ValueError(
            "Unknown completed challenges: "
            f"{sorted(unknown_completed)}"
        )

    completed_count = len(
        data["progress"]["completed_challenges"]
    )

    recorded_total = (
        data["progress"]["total_challenges_completed"]
    )

    if completed_count != recorded_total:
        raise ValueError(
            "Completed challenge count mismatch: "
            f"{completed_count} IDs but "
            f"total_challenges_completed is "
            f"{recorded_total}"
        )

    completion_ids = {
        completion["challenge_id"]
        for completion in data["completions"]
    }

    if completion_ids != completed_ids:
        raise ValueError(
            "Completion history does not match "
            "completed challenges: "
            f"history={sorted(completion_ids)}, "
            f"completed={sorted(completed_ids)}"
        )

    evidence_ids = {
        record["challenge_id"]
        for record in data["evidence"]
    }

    if evidence_ids != completed_ids:
        raise ValueError(
            "Learning evidence does not match "
            "completed challenges: "
            f"evidence={sorted(evidence_ids)}, "
            f"completed={sorted(completed_ids)}"
        )

    required_progress_keys = {
        "completed_challenges",
        "total_challenges_completed",
    }

    missing = (
        required_progress_keys
        - data["progress"].keys()
    )

    if missing:
        raise ValueError(
            f"Missing progress keys: {missing}"
        )

    if not isinstance(
        data["completions"],
        list
    ):
        raise ValueError(
            "completions.json must contain a list."
        )

    if not isinstance(
        data["evidence"],
        list
    ):
        raise ValueError(
            "evidence.json must contain a list."
        )

    print()
    print("✅ All project data is valid.")
    print()


if __name__ == "__main__":
    main()
