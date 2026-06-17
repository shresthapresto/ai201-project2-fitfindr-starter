"""
style_profile.py

Saves and loads user style preferences between sessions.
"""

import json
import os

PROFILE_PATH = "style_profile.json"


def load_profile() -> dict:
    """Load the user's style profile from disk, or return a blank one."""
    if not os.path.exists(PROFILE_PATH):
        return {"favorite_styles": [], "avoided_styles": [], "preferred_sizes": [], "max_budget": None}
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)


def save_profile(profile: dict) -> None:
    """Save the user's style profile to disk."""
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)


def update_profile_from_session(session: dict) -> None:
    """
    After a successful session, update the profile with what the user searched for.
    Adds style tags from the selected item to favorite_styles.
    """
    if session.get("error") or not session.get("selected_item"):
        return

    profile = load_profile()
    item = session["selected_item"]

    for tag in item.get("style_tags", []):
        if tag not in profile["favorite_styles"]:
            profile["favorite_styles"].append(tag)

    if session["parsed"].get("size"):
        size = session["parsed"]["size"]
        if size not in profile["preferred_sizes"]:
            profile["preferred_sizes"].append(size)

    if session["parsed"].get("max_price"):
        profile["max_budget"] = session["parsed"]["max_price"]

    save_profile(profile)


def get_profile_summary() -> str:
    """Return a readable summary of the user's style profile."""
    profile = load_profile()

    if not any(profile.values()):
        return "No style profile yet."

    parts = []
    if profile["favorite_styles"]:
        parts.append(f"Favorite styles: {', '.join(profile['favorite_styles'])}")
    if profile["preferred_sizes"]:
        parts.append(f"Preferred sizes: {', '.join(profile['preferred_sizes'])}")
    if profile["max_budget"]:
        parts.append(f"Usual budget: under ${profile['max_budget']}")

    return "\n".join(parts)