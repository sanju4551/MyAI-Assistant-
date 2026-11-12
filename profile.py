
import json
from pathlib import Path

PROFILE_FILE = Path(__file__).parent / "myai_profile.json"


def load_profile():
    if PROFILE_FILE.exists():
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "name": "",
        "learning_goals": [],
        "explanation_style": "Simple and beginner-friendly"
    }


def save_profile(profile):
    with open(PROFILE_FILE, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4)
