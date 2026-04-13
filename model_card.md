# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use and Non-Intended Use

**Intended use:** VibeFinder suggests the top 5 songs from a 20-song catalog that best match a listener's stated taste for a single session. It is designed for classroom exploration of how content-based recommender systems work.

**Not intended for:** Real users, real products, or any deployment where recommendations affect what people actually listen to. The catalog is too small (20 songs), the features are too coarse (no listening history, no audio analysis), and the weights were tuned by hand for a simulation — not validated against real listener data. It should not be used to make decisions about music licensing, artist promotion, or content curation.

---

## 3. How the Model Works

For every song in the catalog, the system computes a score by comparing four features to the user's preferences:

- **Genre**: If the song's genre matches what the user wants, it earns the most points (3 out of a possible 8.5). Genre is treated as a hard preference — a jazz fan should almost never get metal recommendations.
- **Mood**: If the song's mood matches, it earns the second-highest points (2 out of 8.5). Mood is important but slightly more flexible than genre.
- **Energy**: Instead of rewarding the highest-energy song, the system rewards the *closest* match. A user who wants medium energy gets penalized equally for songs that are too quiet or too loud. This earns up to 2 points.
- **Acoustic texture**: If the song's acoustic character (organic vs. electronic sound) matches the user's preference, it earns 1.5 points.

The song with the highest total score across all four components wins. The top 5 are returned as recommendations, each with a breakdown explaining exactly how the score was earned.

---

## 4. Data

The catalog contains 20 songs stored in `data/songs.csv`. Each song has a title, artist, genre, mood, energy level (0.0–1.0), tempo in BPM, and three audio texture measures: acousticness, danceability, and valence.

The catalog was expanded from the original 10-song starter to 20 songs to cover a wider range of genres and moods. It now includes pop, lofi, rock, synthwave, indie pop, jazz, ambient, electronic, r&b, classical, hip-hop, country, blues, metal, latin, soul, and folk.

Despite the expansion, the dataset still reflects a mostly Western and English-language taste. Every song is a fictional entry written for this simulation. Genres like reggae, K-pop, Afrobeats, and classical Indian music are not represented at all, which means users who prefer those styles will always receive fallback recommendations based on mood and energy alone.

---

## 5. Strengths

The system works best for users whose preferences align tightly with the catalog. In testing:

- The **Chill Lofi Study** profile (lofi / chill / 0.40 energy) produced a near-perfect top result: *Midnight Coding* scored 8.46 out of 8.5, matching on all four dimensions.
- The **Deep Intense Rock** profile found *Storm Runner* at 8.48/8.5 — almost a perfect score.
- The scoring breakdown makes every recommendation fully explainable. A user can see exactly why *Midnight Coding* outranked *Spacewalk Thoughts* — the genre match alone accounts for the gap.
- The proximity formula for energy prevents extreme songs from dominating. A user who wants energy 0.4 will not be flooded with high-energy tracks just because there are more of them in the catalog.

---

## 6. Limitations and Bias

**Genre lock**: Because genre carries the most weight (3 out of 8.5 points), users who prefer a well-represented genre like lofi or pop will always see the same 2–3 songs at the top, regardless of energy or mood variation. The system has no way to introduce diversity unless the genre weight is reduced.

**Missing genres**: Any genre not in the catalog — reggae, K-pop, Afrobeats — earns zero genre points for every song. The system silently falls back to mood and energy matching, and the maximum achievable score drops from 8.5 to 5.5. There is no warning to the user that their preferred genre does not exist.

**Binary acoustic scoring**: Acousticness is treated as a yes/no decision at the 0.5 threshold. A song with acousticness 0.48 scores zero for acoustic even though it is nearly as organic as one at 0.52. This is an artifact of the coarse binary rule, not a genuine difference in character.

**Catalog sparsity**: With only 1–2 songs per genre in most cases, the system feels repetitive quickly. A lofi listener will receive the same three songs every session.

**No session memory**: The recommender starts from scratch every time. It has no way to know a listener just heard three lofi songs and might want variety now.

---

## 7. Evaluation

Six user profiles were tested:

1. **High-Energy Pop** (pop / happy / 0.8): *Sunrise City* scored 8.46/8.5 — a near-perfect match. The score gap to #4 (3.40) confirmed that genre+mood alignment is the dominant signal.

2. **Chill Lofi Study** (lofi / chill / 0.4): Top 3 results were all lofi songs. *Focus Flow* (lofi / focused) ranked above *Spacewalk Thoughts* (ambient / chill) due to genre weight — even though the ambient song matched the mood better.

3. **Deep Intense Rock** (rock / intense / 0.9): *Storm Runner* scored 8.48/8.5. The second-ranked song (*Gym Hero*) was pop/intense — showing that mood match alone can push a song into the top 2.

4. **Adversarial — High-Energy Sad Blues**: The only blues/sad song has energy 0.30, far from the requested 0.90. It still ranked #1 (7.30/8.5) because genre+mood points (5.0) outweighed the energy mismatch penalty (~1.20 lost points). The system chose genre/mood loyalty over energy accuracy.

5. **Adversarial — Reggae (missing genre)**: All songs scored zero for genre. The best achievable score was 5.26 (*Ember & Ash*, soul/peaceful). The system gracefully degraded to mood+energy matching.

6. **Adversarial — Metal Fan Who Wants Quiet Acoustic**: *Iron Crown* ranked #1 at 5.66/8.5 despite having energy 0.97 (vs. target 0.30) and acousticness 0.04. Genre+mood weight (5.0 pts) dominated even with a 1.34-point energy penalty and 0 acoustic points. This was the most surprising result — a song that is almost the opposite of what the user described numerically still "won" on categorical matching.

**Weight-shift experiment**: Doubling the energy weight (to 4.0) and halving the genre weight (to 1.5) caused *Rooftop Lights* (indie pop/happy) to swap positions with *Gym Hero* (pop/intense). Rooftop Lights has energy 0.76 — much closer to the target 0.80 — while Gym Hero has energy 0.93. With higher energy weight, closeness mattered more than sharing the same genre.

---

## 8. Future Work

- **Proximity-based acoustic scoring**: Replace the hard 0.5 threshold with a continuous proximity formula (`1.0 − |user_target − song.acousticness|`), so songs near the boundary are not unfairly penalized.
- **Diversity bonus**: Add a penalty for songs whose genre appears more than once already in the top-k, to surface more variety.
- **Recently played penalty**: Subtract points from songs heard in the last N sessions so the same three lofi songs don't appear every time.
- **Tempo and valence scoring**: The catalog already has `tempo_bpm` and `valence` fields. Adding them to the score formula would improve discrimination between songs that currently tie on genre, mood, and energy.
- **Expand the catalog**: 20 songs is too few for meaningful diversity. Adding 100+ songs across underrepresented genres (reggae, Afrobeats, K-pop) would reduce the "genre lock" problem significantly.

---

## 9. Personal Reflection

**Biggest learning moment:** The adversarial metal profile was the turning point. A user who explicitly asked for quiet acoustic music still got the one loud, electric metal song as their top recommendation — because genre and mood weight (5 out of 8.5 points) overrode the numeric mismatch entirely. That result looked wrong, but the math was correct. It made me realize that "working correctly" and "giving a good answer" are not the same thing. The weights are a design choice, not a fact.

**How AI tools helped — and when I needed to double-check:** AI tools were useful for generating the 20-song catalog and explaining how content-based filtering works in plain language. But I had to verify every generated song value manually — several early drafts had energy or acousticness values outside the valid 0–1 range, and one song had a genre label that didn't match its mood description. AI-generated data needs the same review as any other data source; it can be plausible-sounding but still wrong in ways that quietly break the math.

**What surprised me about simple algorithms:** The recommendations feel surprisingly natural even though the entire system is just four multiplications and a sort. When *Midnight Coding* scores 8.46/8.5 and comes back as the top result for a lofi/chill/acoustic listener, it genuinely seems like a good pick — not like a formula. That gap between "how it works" and "how it feels" is what makes recommender systems easy to anthropomorphize. The algorithm does not "know" anything; it just finds the closest match in feature space.

**What I would try next:** I'd replace the binary acoustic threshold with a continuous proximity score, add a diversity bonus that penalizes repeated genres in the top 5, and expand the catalog to at least 100 songs so genre lock stops dominating every result. I'd also try adding valence (emotional positivity) as a scored feature — the catalog already has the data, and it would help distinguish "sad acoustic" from "peaceful acoustic" which currently score identically on three of four dimensions.
