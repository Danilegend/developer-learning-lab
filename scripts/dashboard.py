#!/usr/bin/env python3

import json
import re
from pathlib import Path
from datetime import date

# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CHALLENGES_FILE = BASE_DIR / "challenges" / "challenges.json"
PROGRESS_FILE = BASE_DIR / "challenges" / "progress.json"
COMPLETIONS_FILE = BASE_DIR / "challenges" / "completions.json"

DASHBOARD_DIR = BASE_DIR / "dashboard"
OUTPUT_FILE = DASHBOARD_DIR / "index.html"


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def progress_bar(percent, width=20):
    filled = round(percent / 100 * width)
    return "█" * filled + "░" * (width - filled)

def load_today_challenge():
    """Load today's generated challenge from Markdown."""

    today = date.today().isoformat()

    daily_file = BASE_DIR / "daily" / f"{today}.md"

    if not daily_file.exists():
        return None

    content = daily_file.read_text(
        encoding="utf-8"
    )

    challenge_id_match = re.search(
        r"\*\*Challenge ID:\*\*\s*([A-Za-z0-9_-]+)",
        content
    )

    focus_match = re.search(
        r"## 🎯 Focus\s*\n\s*(.+)",
        content
    )

    title_match = re.search(
        r"### (.+)",
        content
    )

    difficulty_match = re.search(
        r"\*\*Difficulty:\*\*\s*(.+)",
        content
    )

    objective_match = re.search(
        r"\*\*Difficulty:\*\*.+?\n\n(.+?)(?=\n\n##)",
        content,
        re.DOTALL
    )

    return {
        "date": today,
        "challenge_id": (
            challenge_id_match.group(1)
            if challenge_id_match
            else ""
        ),
        "technology": (
            focus_match.group(1).strip()
            if focus_match
            else ""
        ),
        "title": (
            title_match.group(1).strip()
            if title_match
            else ""
        ),
        "difficulty": (
            difficulty_match.group(1).strip()
            if difficulty_match
            else ""
        ),
        "objective": (
            objective_match.group(1).strip()
            if objective_match
            else ""
        ),
    }

def technology_name(name):
    names = {
        "python": "Python",
        "javascript": "JavaScript",
        "linux": "Linux",
        "git": "Git",
        "sql": "SQL",
        "networking": "Networking",
        "react": "React",
        "nodejs": "Node.js",
        "azure": "Azure",
        "windows": "Windows",
        "security": "Security",
    }

    return names.get(name, name.title())


def calculate_streak(completions):
    """Calculate current and longest learning streak."""

    learning_dates = sorted(
        {
            completion.get("date")
            for completion in completions
            if completion.get("date")
        }
    )

    if not learning_dates:
        return {
            "current": 0,
            "longest": 0,
            "learning_days": 0,
        }

    dates = [
        date.fromisoformat(day)
        for day in learning_dates
    ]

    longest = 1
    current = 1

    streak = 1

    for index in range(1, len(dates)):

        difference = (
            dates[index] - dates[index - 1]
        ).days

        if difference == 1:
            streak += 1
        else:
            streak = 1

        longest = max(longest, streak)

    # Calculate current streak.
    today = date.today()

    if dates[-1] == today:
        current = 1

        for index in range(
            len(dates) - 1,
            0,
            -1
        ):

            difference = (
                dates[index] - dates[index - 1]
            ).days

            if difference == 1:
                current += 1
            else:
                break

    else:
        current = 0

    return {
        "current": current,
        "longest": longest,
        "learning_days": len(dates),
    }


# --------------------------------------------------
# Dashboard generation
# --------------------------------------------------

# --------------------------------------------------
# Dashboard generation
# --------------------------------------------------

def generate_dashboard():

    challenges = load_json(CHALLENGES_FILE)
    progress = load_json(PROGRESS_FILE)
    completions = load_json(COMPLETIONS_FILE)
    
    streak = calculate_streak(completions)

    today_challenge = load_today_challenge()

    total_challenges = sum(
        len(items)
        for items in challenges.values()
    )

    completed = len(completions)

    overall_percent = (
        round((completed / total_challenges) * 100)
        if total_challenges
        else 0
    )

    current_level = progress.get(
        "level",
        "Foundation"
    )

    DASHBOARD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # Technology cards
    # --------------------------------------------------

    technology_cards = ""

    for technology, challenge_list in challenges.items():

        total = len(challenge_list)

        completed_for_technology = sum(
            1
            for completion in completions
            if completion.get("technology") == technology
        )

        percent = (
            round(
                (completed_for_technology / total) * 100
            )
            if total
            else 0
        )

        technology_cards += f"""
        <div class="tech-card">

            <div class="tech-header">
                <h3>{technology_name(technology)}</h3>
                <span>{percent}%</span>
            </div>

            <div class="bar">
                <div
                    class="bar-fill"
                    style="width: {percent}%"
                ></div>
            </div>

            <p>
                {completed_for_technology}
                / {total} challenges completed
            </p>

        </div>
        """

    # --------------------------------------------------
    # Completion history
    # --------------------------------------------------

    completion_rows = ""

    for completion in reversed(completions):

        completion_rows += f"""
        <tr>
            <td>{completion.get("date", "")}</td>

            <td>
                {technology_name(
                    completion.get("technology", "")
                )}
            </td>

            <td>
                {completion.get("title", "")}
            </td>

            <td>
                <span class="completed">
                    ✓ Completed
                </span>
            </td>
        </tr>
        """

    if not completion_rows:

        completion_rows = """
        <tr>
            <td colspan="4">
                No challenges completed yet.
            </td>
        </tr>
        """
    # --------------------------------------------------
    # Today's challenge
    # --------------------------------------------------

    if today_challenge:

        today_challenge_html = f"""
        <section class="today-challenge">

            <div class="today-header">

                <div>

                    <span class="today-label">
                        🎯 TODAY'S CHALLENGE
                    </span>

                    <h2>
                        {today_challenge["title"]}
                    </h2>

                </div>

                <span class="difficulty">
                    {today_challenge["difficulty"]}
                </span>

            </div>

            <div class="today-meta">

                <span>
                    📅 {today_challenge["date"]}
                </span>

                <span>
                    🛠️ {today_challenge["technology"]}
                </span>

                <span>
                    🆔 {today_challenge["challenge_id"]}
                </span>

            </div>

            <p class="objective">

                {today_challenge["objective"]}

            </p>

        </section>
        """

    else:

        today_challenge_html = """
        <section class="today-challenge">

            <h2>
                🎯 Today's Challenge
            </h2>

            <p>
                No challenge has been generated for today.
            </p>

        </section>
        """
    # --------------------------------------------------
    # HTML
    # --------------------------------------------------

    html = f"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Developer Learning Lab</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    font-family:
        Inter,
        Arial,
        sans-serif;

    background: #f5f7fb;

    color: #1f2937;

}}

.container {{

    max-width: 1200px;

    margin: auto;

    padding: 40px 20px;

}}

.hero {{

    background:
        linear-gradient(
            135deg,
            #111827,
            #374151
        );

    color: white;

    border-radius: 20px;

    padding: 40px;

    margin-bottom: 30px;

}}

.hero h1 {{

    margin: 0 0 10px;

    font-size: 36px;

}}

.hero p {{

    margin: 0;

    opacity: 0.8;

}}

.today-challenge {{

    background: white;

    border-radius: 18px;

    padding: 30px;

    margin-bottom: 30px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,0.06);

}}

.today-header {{


    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    gap: 20px;

}} 



.today-label {{


    font-size: 13px;

    font-weight: bold;

    letter-spacing: 1px;

    color: #6b7280;

}}

.today-header h2 {{


    margin:
        8px
        0
        0;

}}

.difficulty {{


    background: #f3f4f6;

    padding:
        6px
        12px;

    border-radius: 20px;

    font-size: 13px;

    font-weight: bold;

}}

.today-meta {{


    display: flex;

    flex-wrap: wrap;

    gap: 20px;

    margin-top: 20px;

    color: #6b7280;

    font-size: 14px;

}}

.objective {{


    margin-top: 20px;

    font-size: 16px;

    line-height: 1.6;

}}

.stats {{

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                200px,
                1fr
            )
        );

    gap: 20px;

    margin-bottom: 30px;

}}

.stat {{

    background: white;

    border-radius: 16px;

    padding: 25px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,0.06);

}}

.stat h2 {{

    margin: 0;

    font-size: 32px;

}}

.stat p {{

    margin-bottom: 0;

    color: #6b7280;

}}

.section {{

    margin-top: 35px;

}}

.section h2 {{

    margin-bottom: 20px;

}}

.tech-grid {{

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                280px,
                1fr
            )
        );

    gap: 20px;

}}

.tech-card {{

    background: white;

    padding: 20px;

    border-radius: 16px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,0.05);

}}

.tech-header {{

    display: flex;

    justify-content: space-between;

    align-items: center;

}}

.tech-header h3 {{

    margin: 0;

}}

.tech-header span {{

    font-weight: bold;

}}

.bar {{

    height: 10px;

    background: #e5e7eb;

    border-radius: 10px;

    overflow: hidden;

    margin-top: 15px;

}}

.bar-fill {{

    height: 100%;

    background: #111827;

    border-radius: 10px;

}}

.tech-card p {{

    color: #6b7280;

    font-size: 14px;

}}

table {{

    width: 100%;

    border-collapse: collapse;

    background: white;

    border-radius: 16px;

    overflow: hidden;

}}

th,
td {{

    padding: 16px;

    text-align: left;

    border-bottom:
        1px solid #e5e7eb;

}}

th {{

    background: #f9fafb;

}}

.completed {{

    color: #166534;

    font-weight: bold;

}}

.footer {{

    margin-top: 40px;

    text-align: center;

    color: #6b7280;

    font-size: 14px;

}}

@media (max-width: 600px) {{

    .hero h1 {{

        font-size: 28px;

    }}

    th,
    td {{

        padding: 10px;

        font-size: 13px;

    }}

}}

</style>

</head>

<body>

<div class="container">

    <section class="hero">

        <h1>
            🚀 Developer Learning Lab
        </h1>

        <p>
            Personal Developer Learning Dashboard
        </p>

    </section>
   
    <section class="hero">

        <h1>
            🚀 Developer Learning Lab
        </h1>

        <p>
            Personal Developer Learning Dashboard
        </p>

    </section>


    {today_challenge_html}


    <section class="stats">

    <section class="stats">

        <div class="stat">

            <h2>
                {current_level}
            </h2>

            <p>
                Current Level
            </p>

        </div>


        <div class="stat">

            <h2>
                {completed}
            </h2>

            <p>
                Challenges Completed
            </p>

        </div>


        <div class="stat">

            <h2>
                {total_challenges}
            </h2>

            <p>
                Total Challenges
            </p>

        </div>


        <div class="stat">

            <h2>
                {overall_percent}%
            </h2>

            <p>
                Overall Progress
            </p>

        </div>

    </section>


    <section class="section">

        <h2>
            📚 Technology Progress
        </h2>

        <div class="tech-grid">

            {technology_cards}

        </div>

    </section>

    <section class="section">

        <h2>
            🔥 Learning Streak
        </h2>

        <div class="stats">

            <div class="stat">

                <h2>
                    🔥 {streak["current"]}
                </h2>

                <p>
                    Current Streak
                </p>

            </div>


            <div class="stat">

                <h2>
                    🏆 {streak["longest"]}
                </h2>

                <p>
                    Longest Streak
                </p>

            </div>


            <div class="stat">

                <h2>
                    📅 {streak["learning_days"]}
                </h2>

                <p>
                    Learning Days
                </p>

            </div>

        </div>

    </section>



    <section class="section">

        <h2>
            🏆 Completed Challenges
        </h2>

        <table>

            <thead>

                <tr>

                    <th>
                        Date
                    </th>

                    <th>
                        Technology
                    </th>

                    <th>
                        Challenge
                    </th>

                    <th>
                        Status
                    </th>

                </tr>

            </thead>

            <tbody>

                {completion_rows}

            </tbody>

        </table>

    </section>


    <div class="footer">

        Generated automatically by
        Developer Learning Lab

        <br>

        Last generated:
        {date.today().isoformat()}

    </div>

</div>

</body>

</html>
"""

    # --------------------------------------------------
    # Write dashboard
    # --------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)

    print(
        f"✅ Dashboard generated: {OUTPUT_FILE}"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    generate_dashboard()
