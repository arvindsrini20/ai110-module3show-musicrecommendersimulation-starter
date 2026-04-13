"""
Research script: How do major streaming platforms predict what users will love?
Uses the Claude API to generate a structured summary of recommendation algorithms,
covering collaborative filtering, content-based filtering, and the key data types
that power these systems (likes, skips, playlists, tempo, mood, etc.).

Also includes analyze_song_features(), which reads data/songs.csv and asks Claude
which attributes are most effective for a content-based recommender, with a
"vibe alignment" evaluation grounded in the actual dataset values.

Also includes design_algorithm_recipe(), which asks Claude to derive a concrete
math-based scoring rule (proximity scoring for numerics, weighted categoricals)
and explains the difference between a scoring rule and a ranking rule.

Also includes critique_user_profile(), which sends a concrete UserProfile + the
full scored ranking to Claude and asks whether the profile is too narrow, whether
it can differentiate intense rock from chill lofi, and what biases to expect.

Also includes design_scoring_weights(), which asks Claude to justify or adjust the
genre/mood/energy/acoustic weights using the expanded 20-song catalog.

Usage:
    ANTHROPIC_API_KEY=your_key python src/research_recommendations.py
    ANTHROPIC_API_KEY=your_key python src/research_recommendations.py --analyze
    ANTHROPIC_API_KEY=your_key python src/research_recommendations.py --recipe
    ANTHROPIC_API_KEY=your_key python src/research_recommendations.py --critique
    ANTHROPIC_API_KEY=your_key python src/research_recommendations.py --weights
"""

import sys
import csv
import pathlib
import anthropic
from pydantic import BaseModel, Field
from typing import List


RESEARCH_PROMPT = """
You are a music technology researcher. Please provide a clear, structured summary
answering the following question:

How do major streaming platforms (Spotify, YouTube Music, Apple Music) predict
what songs users will love next?

Structure your answer with these four sections:

1. COLLABORATIVE FILTERING
   - What it is (using other users' behavior)
   - How it works technically (matrix factorization, nearest-neighbor, etc.)
   - Concrete example of signal data used (plays, skips, playlist adds, likes)
   - Strengths and weaknesses

2. CONTENT-BASED FILTERING
   - What it is (using intrinsic song attributes)
   - How it works technically (feature vectors, similarity scores)
   - Key audio/metadata features: tempo (BPM), mood/valence, energy, danceability,
     acousticness, genre, artist
   - Strengths and weaknesses

3. HYBRID APPROACHES
   - How platforms combine both methods
   - Role of deep learning and session context (e.g., Spotify's BaRT, YouTube's
     two-tower neural models)

4. KEY DATA TYPES SUMMARY TABLE
   Present a concise table with two columns:
   | Data Type        | Category             |
   Rows should include: play count, skip, like/heart, playlist add, share,
   listen duration, BPM/tempo, mood/valence, energy level, danceability,
   acousticness, genre tag, artist, time of day, device type.

Keep the total response under 600 words. Be concrete and educational.
"""


def research_streaming_recommendations() -> None:
    client = anthropic.Anthropic()

    print("Querying Claude about streaming platform recommendation algorithms...\n")
    print("=" * 70)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=64000,
        thinking={"type": "adaptive"},
        system=(
            "You are a concise music technology educator. "
            "Provide structured, accurate summaries grounded in real industry practice. "
            "Use plain language suitable for a software engineering student."
        ),
        messages=[{"role": "user", "content": RESEARCH_PROMPT}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_start":
                if event.content_block.type == "thinking":
                    pass  # skip printing thinking blocks
            elif event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

    final = stream.get_final_message()
    print("\n" + "=" * 70)
    print(
        f"\nTokens used — input: {final.usage.input_tokens}, "
        f"output: {final.usage.output_tokens}"
    )


def analyze_song_features() -> None:
    """
    Read data/songs.csv, send the full dataset to Claude, and ask which features
    are most effective for a simple content-based recommender. Also asks Claude
    to evaluate whether those features capture the intuitive notion of musical
    'vibe' (mood + energy + sonic texture).
    """
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "songs.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found.")
        return

    # Read CSV into a formatted string to embed in the prompt
    with open(csv_path, newline="") as f:
        csv_text = f.read().strip()

    # Build a statistical snapshot so Claude has range/variance context
    rows = list(csv.DictReader(csv_text.splitlines()))
    numeric_cols = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]
    stats_lines = []
    for col in numeric_cols:
        vals = [float(r[col]) for r in rows]
        stats_lines.append(
            f"  {col}: min={min(vals):.2f}, max={max(vals):.2f}, "
            f"mean={sum(vals)/len(vals):.2f}"
        )
    stats_block = "\n".join(stats_lines)

    genres  = sorted({r["genre"]  for r in rows})
    moods   = sorted({r["mood"]   for r in rows})

    prompt = f"""
Below is the full songs.csv dataset from a music recommender simulation project.
It contains {len(rows)} songs with these columns:
  id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness

--- DATASET ---
{csv_text}
--- END DATASET ---

--- NUMERIC FEATURE RANGES (across all {len(rows)} songs) ---
{stats_block}

Categorical values present:
  genres : {", ".join(genres)}
  moods  : {", ".join(moods)}

Please answer the following three questions in order:

QUESTION 1 — FEATURE EFFECTIVENESS
For a simple content-based recommender that scores each song against a user
preference profile, rank ALL available numeric and categorical features by their
expected effectiveness. For each feature explain in one sentence WHY it predicts
user preference well or poorly, referencing the actual ranges shown above.
Format as a ranked list:
  1. <feature>: <reason>
  2. <feature>: <reason>
  ...

QUESTION 2 — MINIMUM VIABLE FEATURE SET
Which 3–4 features form the strongest minimum viable set? Explain the intuition
behind that specific combination — what musical dimension does each one capture?

QUESTION 3 — VIBE ALIGNMENT EVALUATION
A "vibe" is the emotional/sonic feeling a listener seeks in a listening session
(e.g., "chill study music" vs "hype gym session" vs "melancholy late-night drive").
Evaluate how well this dataset's features capture vibe:
  - Which features directly encode vibe? Which only partially?
  - What is MISSING from this dataset that would improve vibe matching?
  - Give one concrete example: pick two songs from the dataset that would feel
    like the SAME vibe and explain which feature values make them similar.
  - Give one concrete example: pick two songs that look numerically close but
    would feel like DIFFERENT vibes in practice, and explain why.

Keep the total answer under 500 words. Be specific about the actual values in
the dataset.
"""

    client = anthropic.Anthropic()
    print("\nAnalyzing songs.csv features with Claude...\n")
    print("=" * 70)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=64000,
        thinking={"type": "adaptive"},
        system=(
            "You are a music recommender systems expert and music theorist. "
            "Give concrete, data-grounded answers. Reference specific songs and "
            "numeric values from the dataset when making comparisons. "
            "Write for a student building their first recommender system."
        ),
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

    final = stream.get_final_message()
    print("\n" + "=" * 70)
    print(
        f"\nTokens used — input: {final.usage.input_tokens}, "
        f"output: {final.usage.output_tokens}"
    )


ALGORITHM_RECIPE_PROMPT = """
You are helping a student design the "Algorithm Recipe" for a simple content-based
music recommender. The system has a UserProfile and a Song object. Each Song has:
  - genre      (string, e.g. "lofi", "rock", "pop")
  - mood       (string, e.g. "chill", "intense", "happy", "relaxed", "focused", "moody")
  - energy     (float 0.0–1.0)
  - tempo_bpm  (float 60–160)
  - valence    (float 0.0–1.0)
  - danceability (float 0.0–1.0)
  - acousticness (float 0.0–1.0)

The UserProfile stores:
  - favorite_genre  (string)
  - favorite_mood   (string)
  - target_energy   (float 0.0–1.0)
  - likes_acoustic  (bool)

Answer the following four questions in order. Be concrete and show real math.

─────────────────────────────────────────────────────────────────────────────
QUESTION 1 — PROXIMITY SCORING FOR NUMERIC FEATURES
─────────────────────────────────────────────────────────────────────────────
A naive approach rewards songs with high energy regardless of what the user wants.
Explain why that is wrong, then show the correct approach: a "proximity score"
that gives FULL points when the song matches the user's preference and FEWER
points the further away it is.

Show the formula using energy as the example. Use this exact format:

  proximity_score(user_energy, song_energy) = ?

Then show two worked examples:
  Example A: user_energy=0.8, song_energy=0.82  → score = ?
  Example B: user_energy=0.8, song_energy=0.35  → score = ?

Also explain how to handle tempo_bpm, which is NOT already on a 0–1 scale
(range is 60–160 in this dataset). Show the normalization step.

─────────────────────────────────────────────────────────────────────────────
QUESTION 2 — SCORING CATEGORICAL FEATURES (GENRE AND MOOD)
─────────────────────────────────────────────────────────────────────────────
Genre and mood are strings, not numbers. Show how to score them as a binary
(match = 1, no match = 0) and then show how to use a WEIGHT so that a matching
genre contributes more to the final score than a matching mood.

Make a concrete recommendation: should genre_weight > mood_weight, or the
reverse? Justify your answer in 2–3 sentences using music listening behaviour
as the argument.

─────────────────────────────────────────────────────────────────────────────
QUESTION 3 — COMPOSING THE FULL SONG SCORE
─────────────────────────────────────────────────────────────────────────────
Combine the pieces above into one formula for total_score(user, song).
Use these suggested weights as a starting point and explain the intuition
behind each weight choice:
  w_genre      = 3.0
  w_mood       = 2.0
  w_energy     = 2.0
  w_tempo      = 1.0
  w_valence    = 1.5
  w_acoustic   = 1.0

Write the formula, then work through a complete scored example using:
  User:  favorite_genre="lofi", favorite_mood="chill", target_energy=0.40,
         likes_acoustic=True
  Song:  "Library Rain" — genre="lofi", mood="chill", energy=0.35,
         tempo_bpm=72, valence=0.60, acousticness=0.86

Show every intermediate value and the final score.

─────────────────────────────────────────────────────────────────────────────
QUESTION 4 — SCORING RULE vs. RANKING RULE
─────────────────────────────────────────────────────────────────────────────
A student asks: "I have my score formula — why do I also need a 'ranking rule'?
Isn't the score enough?"

Explain the conceptual difference between:
  - A SCORING RULE: a function that takes (user, one_song) → float
  - A RANKING RULE: a function that takes (user, list_of_songs, k) → top-k list

Use an analogy or a short concrete example to make clear why you cannot build
a working recommender with only one of these two pieces.

Then write the Python function signatures (no implementation, just signatures
with type hints and a one-line docstring) for both rules to make the
distinction tangible.
"""


def design_algorithm_recipe() -> None:
    """
    Ask Claude to derive the math-based scoring and ranking rules that will
    power the music recommender, using the actual Song and UserProfile fields
    from this project.
    """
    client = anthropic.Anthropic()
    print("\nDesigning the Algorithm Recipe with Claude...\n")
    print("=" * 70)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=64000,
        thinking={"type": "adaptive"},
        system=(
            "You are a computer science instructor teaching a student how to build "
            "their first recommender system. Show all maths explicitly. "
            "Use plain Python-style pseudocode where helpful. "
            "Be precise: every formula must be usable directly in code."
        ),
        messages=[{"role": "user", "content": ALGORITHM_RECIPE_PROMPT}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

    final = stream.get_final_message()
    print("\n" + "=" * 70)
    print(
        f"\nTokens used — input: {final.usage.input_tokens}, "
        f"output: {final.usage.output_tokens}"
    )


# ---------------------------------------------------------------------------
# Pydantic models for structured catalog expansion
# ---------------------------------------------------------------------------

class NewSong(BaseModel):
    title: str
    artist: str
    genre: str
    mood: str
    energy: float = Field(ge=0.0, le=1.0)
    tempo_bpm: float = Field(ge=40.0, le=200.0)
    valence: float = Field(ge=0.0, le=1.0)
    danceability: float = Field(ge=0.0, le=1.0)
    acousticness: float = Field(ge=0.0, le=1.0)


class SongCatalog(BaseModel):
    songs: List[NewSong]


def expand_catalog() -> None:
    """
    Ask Claude (via structured outputs) to generate 10 new songs that fill
    genre and mood gaps in the existing songs.csv, then append them to the file.
    """
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "songs.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found.")
        return

    with open(csv_path, newline="") as f:
        existing_text = f.read().strip()

    existing_rows = list(csv.DictReader(existing_text.splitlines()))
    existing_genres = sorted({r["genre"] for r in existing_rows})
    existing_moods  = sorted({r["mood"]  for r in existing_rows})
    next_id         = max(int(r["id"]) for r in existing_rows) + 1

    prompt = f"""
You are expanding a music catalog for a recommender system simulation.

EXISTING CATALOG ({len(existing_rows)} songs):
{existing_text}

GENRES ALREADY PRESENT: {", ".join(existing_genres)}
MOODS ALREADY PRESENT:  {", ".join(existing_moods)}

TASK: Generate exactly 10 new songs that diversify the catalog.

REQUIREMENTS:
1. Every new song must use a genre NOT in the existing list above.
   Good choices: hip-hop, r&b, electronic, classical, country, metal,
   reggae, soul, folk, latin, k-pop, blues, bossa nova, drum and bass.
2. Aim for at least 4 new mood values not yet in the catalog.
   Good choices: sad, melancholy, romantic, nostalgic, angry, peaceful,
   playful, ethereal, gritty, triumphant.
3. Spread the numeric features across the full 0.0–1.0 range — avoid
   clustering all songs near 0.5. Include some extreme values.
4. tempo_bpm should range from 55 (slow ballad) to 175 (fast drum and bass).
5. Make titles and artist names creative and genre-appropriate.
6. All 10 songs must be distinct from each other and from the existing songs.

Return your answer as a JSON object matching the schema provided.
"""

    client = anthropic.Anthropic()
    print("\nGenerating new songs with Claude (structured output)...\n")

    response = client.messages.parse(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=(
            "You are a creative music data generator. "
            "Produce realistic, varied fictional songs. "
            "Return only valid JSON matching the required schema."
        ),
        messages=[{"role": "user", "content": prompt}],
        output_format=SongCatalog,
    )

    catalog: SongCatalog = response.parsed_output

    # Append new rows to songs.csv
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        for i, song in enumerate(catalog.songs):
            row_id = next_id + i
            writer.writerow([
                row_id,
                song.title,
                song.artist,
                song.genre,
                song.mood,
                f"{song.energy:.2f}",
                f"{song.tempo_bpm:.0f}",
                f"{song.valence:.2f}",
                f"{song.danceability:.2f}",
                f"{song.acousticness:.2f}",
            ])

    # Print a summary table of what was added
    print(f"Added {len(catalog.songs)} songs (IDs {next_id}–{next_id + len(catalog.songs) - 1}):\n")
    print(f"{'ID':<4} {'Title':<28} {'Genre':<16} {'Mood':<12} {'Energy':>7} {'BPM':>5}")
    print("-" * 78)
    for i, song in enumerate(catalog.songs):
        print(
            f"{next_id + i:<4} {song.title:<28} {song.genre:<16} {song.mood:<12} "
            f"{song.energy:>7.2f} {song.tempo_bpm:>5.0f}"
        )

    print(f"\nNew genres added : {sorted({s.genre for s in catalog.songs})}")
    print(f"New moods added  : {sorted({s.mood  for s in catalog.songs} - set(existing_moods))}")
    print(f"\ndata/songs.csv now has {len(existing_rows) + len(catalog.songs)} songs total.")
    print(f"\nTokens used — input: {response.usage.input_tokens}, "
          f"output: {response.usage.output_tokens}")


def _load_catalog_with_scores(
    fav_genre: str,
    fav_mood: str,
    target_energy: float,
    likes_acoustic: bool,
) -> tuple[list[dict], list[tuple[dict, float]]]:
    """Load songs.csv and score every song against the given profile."""
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "songs.csv"
    rows = list(csv.DictReader(csv_path.read_text().splitlines()))

    W_GENRE, W_MOOD, W_ENERGY, W_ACOUSTIC = 3.0, 2.0, 2.0, 1.5

    def score_song(r: dict) -> float:
        g = 1.0 if r["genre"] == fav_genre  else 0.0
        m = 1.0 if r["mood"]  == fav_mood   else 0.0
        e = 1.0 - abs(target_energy - float(r["energy"]))
        a = 1.0 if (float(r["acousticness"]) > 0.5) == likes_acoustic else 0.0
        return W_GENRE * g + W_MOOD * m + W_ENERGY * e + W_ACOUSTIC * a

    ranked = sorted(
        [(r, score_song(r)) for r in rows],
        key=lambda x: x[1],
        reverse=True,
    )
    return rows, ranked


def critique_user_profile() -> None:
    """
    Step 2: Send the sample user profile + scored ranking to Claude and ask:
    - Does the profile differentiate 'intense rock' from 'chill lofi'?
    - Is the profile too narrow?
    - What are the most interesting edge cases?
    - What structural biases will this profile introduce?
    """
    rows, ranked = _load_catalog_with_scores(
        fav_genre="lofi",
        fav_mood="chill",
        target_energy=0.40,
        likes_acoustic=True,
    )

    # Build a ranked table string to embed in the prompt
    table_lines = [f"{'Rank':<5}{'Title':<28}{'Genre':<14}{'Mood':<12}{'Score':>6}"]
    table_lines.append("-" * 66)
    for rank, (r, s) in enumerate(ranked, 1):
        table_lines.append(
            f"{rank:<5}{r['title']:<28}{r['genre']:<14}{r['mood']:<12}{s:>6.2f}"
        )
    table_str = "\n".join(table_lines)

    prompt = f"""
A student is building a content-based music recommender with this UserProfile:

  favorite_genre  = "lofi"
  favorite_mood   = "chill"
  target_energy   = 0.40
  likes_acoustic  = True

The scoring formula is:
  total_score = 3.0 × genre_match
              + 2.0 × mood_match
              + 2.0 × (1 − |0.40 − song.energy|)
              + 1.5 × acoustic_match   (1 if acousticness > 0.5 == likes_acoustic)
  Maximum score: 8.5

Here is the full ranked output of all 20 songs for this profile:

{table_str}

Please answer these four questions:

1. DIFFERENTIATION TEST
   Compare the rank-1 song (Midnight Coding, lofi/chill) with Storm Runner
   (rock/intense, rank 17). Is the 7.48-point gap large enough to confidently
   say the profile distinguishes these two listening contexts? What does the
   gap tell us about the weight design?

2. NARROWNESS CRITIQUE
   Identify any songs in the ranked list that a real "chill lofi" listener
   would probably enjoy but that the current formula undervalues. Explain
   the specific feature mismatch causing the undervaluation.

3. EDGE CASES
   Focus Flow (lofi/focused) ranks #3 with score 6.50, above Spacewalk
   Thoughts (ambient/chill) at #4 with 5.26. Does this ranking feel right
   for a user who asked for "chill" music? Diagnose which weight is
   responsible for this ordering and whether it should be adjusted.

4. EXPECTED BIASES
   Based on this profile and formula, list three concrete biases a user would
   notice after a few recommendation cycles (e.g., "the system will always
   recommend the same 3 lofi songs"). For each bias, suggest one small change
   to the profile or the weights that would mitigate it.

Be specific: reference song titles, genres, moods, and score values.
"""

    client = anthropic.Anthropic()
    print("\nCritiquing the user profile with Claude...\n")
    print("=" * 70)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=64000,
        thinking={"type": "adaptive"},
        system=(
            "You are a recommender systems educator reviewing a student's first "
            "content-based recommender. Be honest and constructive. "
            "Ground every claim in the actual score values shown."
        ),
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

    final = stream.get_final_message()
    print("\n" + "=" * 70)
    print(f"\nTokens — input: {final.usage.input_tokens}, output: {final.usage.output_tokens}")


def design_scoring_weights() -> None:
    """
    Step 3: Ask Claude to evaluate and justify the genre/mood/energy/acoustic
    weights using the full 20-song catalog, contrasting with the simpler
    '+2 genre, +1 mood' starting point from the module instructions.
    """
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "songs.csv"
    csv_text = csv_path.read_text().strip()

    prompt = f"""
A student is finalizing the scoring weights for a content-based music recommender.

CATALOG (20 songs):
{csv_text}

PROPOSED WEIGHTS (based on algorithm design session):
  w_genre    = 3.0   (binary: genre matches user's favorite_genre)
  w_mood     = 2.0   (binary: mood matches user's favorite_mood)
  w_energy   = 2.0   (proximity: 1 − |target_energy − song.energy|)
  w_acoustic = 1.5   (binary: acousticness > 0.5 matches likes_acoustic)
  ─────────────────────────────────────────────────────
  Max score  = 8.5

MODULE STARTING POINT for comparison:
  w_genre = 2.0, w_mood = 1.0 (with no acoustic or energy term)

Please answer three questions:

1. WEIGHT JUSTIFICATION
   For each of the four weights, explain in one sentence why that weight value
   makes sense given the variety of genres and moods in this specific 20-song
   catalog. Reference at least one song by name per weight.

2. PROPOSED vs STARTING POINT
   The module suggests starting with "+2.0 genre, +1.0 mood, + energy similarity."
   The student's weights are higher (3.0/2.0) and add an acoustic term.
   What practical difference would a user notice between the two formulas
   when the catalog contains both "Requiem for Still Water" (classical, energy=0.19)
   and "Iron Crown" (metal, energy=0.97)?

3. ONE IMPROVEMENT
   Suggest one specific weight change that would make the formula perform better
   across the full diversity of this 20-song catalog. Show a before/after score
   example using songs from the CSV to demonstrate the improvement.
"""

    client = anthropic.Anthropic()
    print("\nDesigning scoring weights with Claude...\n")
    print("=" * 70)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=64000,
        thinking={"type": "adaptive"},
        system=(
            "You are a recommender systems instructor. "
            "Be concrete — every recommendation must reference specific songs, "
            "genres, or score values from the dataset provided."
        ),
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

    final = stream.get_final_message()
    print("\n" + "=" * 70)
    print(f"\nTokens — input: {final.usage.input_tokens}, output: {final.usage.output_tokens}")


if __name__ == "__main__":
    if "--analyze" in sys.argv:
        analyze_song_features()
    elif "--recipe" in sys.argv:
        design_algorithm_recipe()
    elif "--expand" in sys.argv:
        expand_catalog()
    elif "--critique" in sys.argv:
        critique_user_profile()
    elif "--weights" in sys.argv:
        design_scoring_weights()
    else:
        research_streaming_recommendations()
