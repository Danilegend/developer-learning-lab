import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

CHALLENGES_FILE = BASE_DIR / "challenges" / "challenges.json"
PROGRESS_FILE = BASE_DIR / "challenges" / "progress.json"
COMPLETIONS_FILE = BASE_DIR / "challenges" / "completions.json"
EVIDENCE_FILE = BASE_DIR / "evidence" / "evidence.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_all_challenge_ids():
    challenges = load_json(CHALLENGES_FILE)

    return {
        challenge["id"]
        for items in challenges.values()
        for challenge in items
    }


def test_all_required_files_exist():
    assert CHALLENGES_FILE.exists()
    assert PROGRESS_FILE.exists()
    assert COMPLETIONS_FILE.exists()
    assert EVIDENCE_FILE.exists()


def test_completed_challenges_exist():
    challenge_ids = get_all_challenge_ids()
    progress = load_json(PROGRESS_FILE)

    completed = set(progress["completed_challenges"])

    assert completed <= challenge_ids


def test_completion_history_matches_progress():
    progress = load_json(PROGRESS_FILE)
    completions = load_json(COMPLETIONS_FILE)

    completed = set(progress["completed_challenges"])
    completion_ids = {
        item["challenge_id"]
        for item in completions
    }

    assert completion_ids == completed


def test_evidence_matches_completed_challenges():
    progress = load_json(PROGRESS_FILE)
    evidence = load_json(EVIDENCE_FILE)

    completed = set(progress["completed_challenges"])
    evidence_ids = {
        item["challenge_id"]
        for item in evidence
    }

    assert evidence_ids == completed


def test_evidence_contains_required_fields():
    evidence = load_json(EVIDENCE_FILE)

    required_fields = {
        "challenge_id",
        "technology",
        "date",
        "title",
        "difficulty",
        "status",
        "objective",
        "concepts",
    }

    for record in evidence:
        assert required_fields <= record.keys()
        assert record["status"] == "completed"
        assert isinstance(record["concepts"], list)
