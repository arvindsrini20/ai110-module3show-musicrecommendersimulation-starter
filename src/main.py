"""
Command-line runner for the Music Recommender Simulation.

Usage:
    python3 -m src.main               # run all profiles
    python3 -m src.main --experiment  # run weight-shift experiment
"""

import sys
from .recommender import load_songs, recommend_songs, MAX_SCORE


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

PROFILES = [
    {
        "name": "High-Energy Pop",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
    },
    {
        "name": "Chill Lofi Study",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True},
    },
    {
        "name": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    },
    # --- adversarial / edge-case profiles ---
    {
        "name": "Adversarial: High-Energy Sad Blues",
        "prefs": {"genre": "blues", "mood": "sad", "energy": 0.9, "likes_acoustic": True},
        "note": (
            "Conflict: 'sad' mood is almost always low-energy in this catalog "
            "(Worn-Out Shoes Blues has energy=0.30). The system must choose between "
            "honouring the genre+mood match or the energy target."
        ),
    },
    {
        "name": "Adversarial: Genre Not in Catalog (Reggae)",
        "prefs": {"genre": "reggae", "mood": "peaceful", "energy": 0.5, "likes_acoustic": True},
        "note": (
            "Reggae does not exist in the 20-song catalog. "
            "Genre weight (3.0 pts) is wasted for every song. "
            "The system falls back to mood + energy + acoustic matching only."
        ),
    },
    {
        "name": "Adversarial: Metal Fan Who Wants Quiet Acoustic",
        "prefs": {"genre": "metal", "mood": "angry", "energy": 0.3, "likes_acoustic": True},
        "note": (
            "Iron Crown (the only metal/angry song) has energy=0.97 and "
            "acousticness=0.04 — opposite of what this user wants numerically. "
            "Does genre+mood weight (5.0 pts) override the energy/acoustic mismatch?"
        ),
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_profile_results(name: str, prefs: dict, songs: list,
                          note: str = "", max_score: float = MAX_SCORE,
                          weights: dict | None = None) -> None:
    """Print a formatted recommendations block for one profile."""
    print(f"\n{'═' * 62}")
    print(f"  PROFILE: {name}")
    print(f"{'═' * 62}")
    print(
        f"  genre={prefs['genre']} | mood={prefs['mood']} | "
        f"energy={prefs['energy']} | acoustic={prefs.get('likes_acoustic', '—')}"
    )
    if note:
        print(f"\n  ⚠  {note}")
    if weights:
        print(f"\n  Weights: genre={weights.get('W_GENRE',3.0)} | "
              f"mood={weights.get('W_MOOD',2.0)} | "
              f"energy={weights.get('W_ENERGY',2.0)} | "
              f"acoustic={weights.get('W_ACOUSTIC',1.5)}")
    print(f"\n  {'Rank':<5} {'Title':<26} {'Score':>7}  Reasons")
    print(f"  {'─'*58}")

    results = recommend_songs(prefs, songs, k=5, weights=weights)
    for rank, (song, score, explanation) in enumerate(results, 1):
        bar = "█" * int((score / max_score) * 14) + "░" * (14 - int((score / max_score) * 14))
        print(f"\n  #{rank}  {song['title']:<26}  {score:>4.2f}/{max_score:.1f}  [{bar}]")
        print(f"       {song['genre']} / {song['mood']}")
        for reason in explanation.split(" | "):
            print(f"       • {reason}")


# ---------------------------------------------------------------------------
# Experiment: double energy weight, halve genre weight
# ---------------------------------------------------------------------------

def run_experiment(songs: list) -> None:
    """Step 3: compare default weights vs energy-heavy weights for pop/happy."""
    exp_weights = {"W_GENRE": 1.5, "W_MOOD": 2.0, "W_ENERGY": 4.0, "W_ACOUSTIC": 1.5}
    exp_max     = sum(exp_weights.values())   # 9.0

    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    print(f"\n{'═' * 62}")
    print("  EXPERIMENT: Double energy weight, halve genre weight")
    print(f"  Default  → genre=3.0  energy=2.0  (max {MAX_SCORE:.1f})")
    print(f"  Modified → genre=1.5  energy=4.0  (max {exp_max:.1f})")
    print(f"{'═' * 62}")

    default_results  = recommend_songs(prefs, songs, k=5)
    modified_results = recommend_songs(prefs, songs, k=5, weights=exp_weights)

    default_titles  = [r[0]["title"] for r in default_results]
    modified_titles = [r[0]["title"] for r in modified_results]

    print(f"\n  {'Rank':<5} {'Default weights':<28} {'Modified weights':<28}")
    print(f"  {'─'*62}")
    for i in range(5):
        d = f"{default_titles[i]}"
        m = f"{modified_titles[i]}"
        change = "  ←same" if d == m else ""
        print(f"  #{i+1:<4} {d:<28} {m:<28}{change}")

    new_entries = [t for t in modified_titles if t not in default_titles]
    dropped     = [t for t in default_titles  if t not in modified_titles]
    if new_entries:
        print(f"\n  Entered top 5 : {', '.join(new_entries)}")
    if dropped:
        print(f"  Left top 5    : {', '.join(dropped)}")
    print(
        "\n  Insight: Higher energy weight rewards energy closeness over genre loyalty.\n"
        "  Songs with the 'right' energy but wrong genre overtake same-genre songs\n"
        "  whose energy is further from the target."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    if "--experiment" in sys.argv:
        run_experiment(songs)
        return

    for profile in PROFILES:
        print_profile_results(
            name=profile["name"],
            prefs=profile["prefs"],
            songs=songs,
            note=profile.get("note", ""),
        )

    print(f"\n{'═' * 62}\n")


if __name__ == "__main__":
    main()
