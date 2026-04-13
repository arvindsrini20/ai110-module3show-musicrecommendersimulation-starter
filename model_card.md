# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use and Non-Intended Use

**Intended use:** VibeFinder is meant for a classroom setting to show how a basic music recommender works. It looks at a user's preferred genre, mood, energy level, and whether they like acoustic music, then returns the top 5 matching songs from a 20-song catalog.

**Not intended for:** Real users or real products. The catalog only has 20 songs, the weights were set by hand, and the system never learns from actual listening data. It should not be used to make decisions about what music gets promoted or recommended to real people.

---

## 3. How the Model Works

For each song in the catalog, the system gives it a score based on how well it matches what the user wants. There are four things it checks:

- **Genre**: If the song matches the user's genre, it gets 3 points. Genre matters the most because it is the biggest factor in what someone wants to hear.
- **Mood**: A mood match earns 2 points. Mood is important but a little more flexible than genre.
- **Energy**: Instead of just picking the most energetic song, the system picks the one closest to what the user asked for. A perfect energy match earns up to 2 points.
- **Acoustic texture**: If the song's sound (organic vs. electronic) matches what the user likes, it earns 1.5 points.

The scores are added up and the top 5 songs are returned. Each result shows a breakdown of exactly how the score was calculated.

---

## 4. Data

The catalog has 20 songs saved in `data/songs.csv`. Each song has a title, artist, genre, mood, energy (0.0 to 1.0), tempo in BPM, acousticness, danceability, and valence.

The original starter file had 10 songs. I expanded it to 20 to include more variety. The catalog now covers genres like pop, lofi, rock, jazz, ambient, hip-hop, blues, metal, soul, and folk.

That said, the dataset is still pretty limited. All the songs are fictional and reflect mostly Western music styles. Genres like reggae, K-pop, and Afrobeats are not included at all, so users who prefer those styles will never get a genre match.

---

## 5. Strengths

The system works best when the user's preferences match something in the catalog closely. A few examples from testing:

- The **Chill Lofi Study** profile got *Midnight Coding* as the top result with a score of 8.46 out of 8.5. It matched on all four features.
- The **Deep Intense Rock** profile got *Storm Runner* at 8.48/8.5, which was the highest score across all tests.
- Every recommendation comes with an explanation showing exactly which features matched and how many points each one added. This makes the system easy to understand and debug.
- The energy scoring penalizes songs that are too loud OR too quiet, so it actually rewards closeness rather than just high energy.

---

## 6. Limitations and Bias

**Genre lock**: Genre has the highest weight (3 out of 8.5 points), so users who like a genre with only a few songs in the catalog will see the same results every time. A lofi listener will almost always get the same 3 songs at the top.

**Missing genres**: If a user's preferred genre is not in the catalog, they get zero genre points for every song. The max score drops from 8.5 to 5.5 and there is no message telling the user this happened.

**Binary acoustic scoring**: The system decides if a song is acoustic based on whether its acousticness score is above or below 0.5. A song at 0.48 and a song at 0.52 are treated completely differently even though they sound almost the same.

**Small catalog**: With only 1 or 2 songs per genre, the recommendations get repetitive fast.

**No memory**: The system starts fresh every time. It does not know what a user already heard, so it might suggest the same songs over and over.

---

## 7. Evaluation

I tested six user profiles:

1. **High-Energy Pop** (pop / happy / 0.8 energy): *Sunrise City* scored 8.46/8.5. Songs ranked 4th and 5th had scores around 3.4, which shows how much genre and mood matter.

2. **Chill Lofi Study** (lofi / chill / 0.4 energy): The top 3 were all lofi songs. *Focus Flow* ranked above *Spacewalk Thoughts* just because it matched the genre, even though *Spacewalk Thoughts* matched the mood better.

3. **Deep Intense Rock** (rock / intense / 0.9 energy): *Storm Runner* was a near-perfect match. The second place song was pop/intense, which shows mood alone can push a song into the top 2.

4. **Adversarial - High-Energy Sad Blues**: The only blues/sad song has an energy of 0.30, but the user wanted 0.90. It still came in first (7.30/8.5) because genre and mood points added up to 5.0 and outweighed the energy penalty.

5. **Adversarial - Reggae (not in catalog)**: Every song got zero genre points. The best result was 5.26/8.5. The system just quietly fell back to mood and energy matching.

6. **Adversarial - Metal Fan Who Wants Quiet Acoustic**: *Iron Crown* has energy 0.97 and acousticness 0.04, almost the opposite of what this user wanted. It still ranked first at 5.66/8.5 because genre and mood together were worth 5.0 points.

**Weight shift experiment**: I doubled the energy weight and cut the genre weight in half. This caused *Rooftop Lights* and *Gym Hero* to swap at ranks 2 and 3. Rooftop Lights has energy 0.76 (very close to the 0.80 target), while Gym Hero has energy 0.93 (further away). With more emphasis on energy, closeness to the target mattered more than sharing the same genre.

---

## 8. Future Work

- **Smoother acoustic scoring**: Replace the 0.5 cutoff with a formula that gives partial credit based on how close a song's acousticness is to what the user wants.
- **Diversity bonus**: Add a small penalty if the same genre shows up more than once in the top 5, so the results feel less repetitive.
- **More songs**: 20 songs is not enough. Adding 100 or more songs across a wider range of genres would make the recommendations feel more varied and useful.

---

## 9. Personal Reflection

**Biggest learning moment:** The metal profile surprised me the most. The user asked for quiet acoustic music, but the system still returned the loud electric metal song as the top pick. The math was not wrong, but the answer felt wrong. That made me realize that a system can follow its rules perfectly and still give a bad result. The weights are just design decisions, not facts.

**How AI tools helped and when I needed to double-check:** AI tools helped me generate the extra songs for the catalog and helped me understand how content-based filtering works. But I had to manually check every generated song because some had energy or acousticness values outside the 0 to 1 range, and a few had genre labels that did not match their moods. AI output needs review just like any other data.

**What surprised me about simple algorithms:** The results actually feel like real recommendations even though the whole system is just four math operations and a sort. When *Midnight Coding* comes up as the top pick for a lofi/chill listener with a score of 8.46, it genuinely feels like a good suggestion. The gap between how simple the code is and how natural the output feels was something I did not expect going in.

**What I would try next:** I would add continuous acoustic scoring instead of the binary cutoff, add a genre diversity bonus to avoid repetitive results, and expand the catalog to at least 100 songs. I would also try scoring valence (the emotional positivity of a song) since the data is already there and it would help separate "sad acoustic" from "calm acoustic" which currently score the same way.
