import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its audio/metadata attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a listener's taste preferences for a session."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Weights — defined once so they are easy to tune
# ---------------------------------------------------------------------------
W_GENRE    = 3.0   # genre is the hardest listener constraint
W_MOOD     = 2.0   # mood is strong but negotiable
W_ENERGY   = 2.0   # proximity: rewards closeness to target, not raw magnitude
W_ACOUSTIC = 1.5   # organic vs produced texture — binary but meaningful
MAX_SCORE  = W_GENRE + W_MOOD + W_ENERGY + W_ACOUSTIC  # 8.5


# ---------------------------------------------------------------------------
# Step 1 — load_songs
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields converted."""
    FLOAT_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    INT_FIELDS   = {"id"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in FLOAT_FIELDS:
                if field in row:
                    row[field] = float(row[field])
            for field in INT_FIELDS:
                if field in row:
                    row[field] = int(row[field])
            songs.append(dict(row))
    return songs


# ---------------------------------------------------------------------------
# Step 2 — score_song
# ---------------------------------------------------------------------------

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (score, reason_list).

    Supports both short keys ("genre", "mood", "energy") and long keys
    ("favorite_genre", "favorite_mood", "target_energy") so the function
    works with both the functional API and OOP adapters.
    """
    # Normalise key names — accept "genre" or "favorite_genre" etc.
    genre          = user_prefs.get("genre")          or user_prefs.get("favorite_genre", "")
    mood           = user_prefs.get("mood")           or user_prefs.get("favorite_mood",  "")
    target_energy  = user_prefs.get("energy")         or user_prefs.get("target_energy",  0.5)
    likes_acoustic = user_prefs.get("likes_acoustic")  # None → skip acoustic scoring

    score: float    = 0.0
    reasons: List[str] = []

    # Genre match ─────────────────────────────────────────────────────────
    if song["genre"] == genre:
        score += W_GENRE
        reasons.append(f"genre match: {genre} (+{W_GENRE:.1f})")

    # Mood match ──────────────────────────────────────────────────────────
    if song["mood"] == mood:
        score += W_MOOD
        reasons.append(f"mood match: {mood} (+{W_MOOD:.1f})")

    # Energy proximity ────────────────────────────────────────────────────
    # 1.0 when energy == target; approaches 0.0 as the gap grows toward 1.0
    energy_prox = 1.0 - abs(target_energy - song["energy"])
    energy_pts  = round(W_ENERGY * energy_prox, 2)
    score       = round(score + energy_pts, 2)
    reasons.append(
        f"energy {song['energy']:.2f} vs target {float(target_energy):.2f} (+{energy_pts:.2f})"
    )

    # Acoustic texture match ──────────────────────────────────────────────
    if likes_acoustic is not None:
        song_is_acoustic = song["acousticness"] > 0.5
        if song_is_acoustic == bool(likes_acoustic):
            score = round(score + W_ACOUSTIC, 2)
            label = "acoustic" if likes_acoustic else "non-acoustic"
            reasons.append(f"texture match: {label} (+{W_ACOUSTIC:.1f})")

    return score, reasons


# ---------------------------------------------------------------------------
# Step 3 — recommend_songs
# ---------------------------------------------------------------------------

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, then return the top-k results sorted highest first.

    Uses sorted() (returns a new list) rather than list.sort() (mutates in
    place) so the original catalog order is never changed.
    Returns a list of (song_dict, score, explanation_string) tuples.
    """
    scored = [
        (song, *score_song(user_prefs, song))   # (song, score, reasons)
        for song in songs
    ]

    # sorted() key = score (index 1), descending; original `songs` list untouched
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    # Flatten reasons list into a single readable string for the caller
    return [
        (song, score, " | ".join(reasons))
        for song, score, reasons in ranked[:k]
    ]


# ---------------------------------------------------------------------------
# OOP wrapper — Recommender
# ---------------------------------------------------------------------------

def _song_to_dict(song: Song) -> Dict:
    """Convert a Song dataclass to a plain dict compatible with score_song."""
    return {
        "id": song.id, "title": song.title, "artist": song.artist,
        "genre": song.genre, "mood": song.mood,
        "energy": song.energy, "tempo_bpm": song.tempo_bpm,
        "valence": song.valence, "danceability": song.danceability,
        "acousticness": song.acousticness,
    }


def _profile_to_dict(user: UserProfile) -> Dict:
    """Convert a UserProfile dataclass to a plain dict compatible with score_song."""
    return {
        "genre":          user.favorite_genre,
        "mood":           user.favorite_mood,
        "energy":         user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }


class Recommender:
    """OOP interface to the content-based recommender."""

    def __init__(self, songs: List[Song]):
        """Initialise with a list of Song objects."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given user."""
        user_dict  = _profile_to_dict(user)
        song_dicts = [_song_to_dict(s) for s in self.songs]

        ranked_dicts = recommend_songs(user_dict, song_dicts, k=k)

        # Map scored dicts back to the original Song objects by id
        id_to_song = {s.id: s for s in self.songs}
        return [id_to_song[result[0]["id"]] for result in ranked_dicts]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable score breakdown for one (user, song) pair."""
        score, reasons = score_song(_profile_to_dict(user), _song_to_dict(song))
        return f"Score {score:.2f}/{MAX_SCORE:.1f} — " + " | ".join(reasons)
