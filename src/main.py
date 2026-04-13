"""
Command-line runner for the Music Recommender Simulation.

Usage:
    python -m src.main
"""

from .recommender import load_songs, recommend_songs, MAX_SCORE


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = {
        "genre":          "pop",
        "mood":           "happy",
        "energy":         0.8,
        "likes_acoustic": False,
    }

    print(
        f"\nUser profile — genre: {user_prefs['genre']} | "
        f"mood: {user_prefs['mood']} | "
        f"energy: {user_prefs['energy']} | "
        f"likes_acoustic: {user_prefs['likes_acoustic']}"
    )
    print(f"Max possible score: {MAX_SCORE:.1f}\n")
    print("─" * 60)
    print("Top 5 Recommendations")
    print("─" * 60)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        bar_filled = int((score / MAX_SCORE) * 20)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        print(f"\n#{rank}  {song['title']}  —  {song['artist']}")
        print(f"    Score : {score:.2f} / {MAX_SCORE:.1f}  [{bar}]")
        print(f"    Genre : {song['genre']}   Mood: {song['mood']}")
        for reason in explanation.split(" | "):
            print(f"    • {reason}")

    print("\n" + "─" * 60)


if __name__ == "__main__":
    main()
