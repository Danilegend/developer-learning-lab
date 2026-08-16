#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def run_git(command):
    """Run a Git command and return the result."""

    try:
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            text=True,
            capture_output=True,
            check=True
        )

        return result

    except subprocess.CalledProcessError as error:

        print()
        print("❌ Git command failed:")
        print(" ".join(command))

        if error.stdout:
            print()
            print(error.stdout)

        if error.stderr:
            print()
            print(error.stderr)

        return None


def get_status():
    """Return Git status information."""

    result = run_git(
        ["git", "status", "--porcelain"]
    )

    if result is None:
        return None

    return result.stdout.strip()


def create_commit(message):
    """Stage project changes and create a Git commit."""

    status = get_status()

    if status is None:
        return False

    if not status:
        print("ℹ️ No Git changes to commit.")
        return False

    print()
    print("📦 Git changes detected:")
    print(status)

    print()
    print("📥 Staging changes...")

    if run_git(["git", "add", "."]) is None:
        return False

    print("✅ Changes staged.")

    print()
    print("📝 Creating commit...")

    if run_git(
        ["git", "commit", "-m", message]
    ) is None:
        return False

    print("✅ Commit created.")

    return True


def push_to_github():
    """Push the current branch to GitHub."""

    print()
    print("🚀 Pushing to GitHub...")

    result = run_git(
        ["git", "push", "origin", "main"]
    )

    if result is None:
        return False

    print("✅ Push completed.")

    return True


def main():

    commit_message = (
        "chore: update developer learning progress"
    )

    print()
    print("======================================")
    print("       🚀 GIT AUTOMATION")
    print("======================================")

    print()
    print("Repository:")
    print(BASE_DIR)

    print()
    print("Commit message:")
    print(commit_message)

    if not create_commit(commit_message):
        print()
        print("ℹ️ Nothing was committed.")
        return

    if not push_to_github():
        print()
        print(
            "⚠️ Commit created, "
            "but GitHub push failed."
        )
        sys.exit(1)

    print()
    print("🎉 Git automation completed successfully!")


if __name__ == "__main__":
    main()
