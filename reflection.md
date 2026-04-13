# Reflection — Music Recommender Simulation

## What I Built

I built a content-based music recommender that scores every song in a 20-song catalog against a user's stated preferences and returns the top 5 matches. The scoring formula combines four features: genre match, mood match, energy proximity, and acoustic texture. Each feature is weighted so the system reflects how strongly listeners actually care about each dimension — genre is the hardest constraint, so it carries the most weight.

## Profile Comparisons

**High-Energy Pop vs. Chill Lofi Study**
These two profiles produced the clearest results. Both got near-perfect #1 scores (8.46/8.5) for songs that matched on every dimension. The interesting contrast was in how the lower-ranked songs differed: the pop profile's #4 was synthwave/moody because no other pop song was left, while the lofi profile's #4 was ambient/chill — a different genre but the same mood. The lofi profile illustrates genre lock: only 3 of 20 songs are lofi, so the top 3 are always the same titles.

**Deep Intense Rock**
Storm Runner scored 8.48/8.5 — the highest score in any test. This profile showed that when a genre is well-represented and the catalog has a matching song with the right energy, the system works exactly as intended.

**Adversarial: High-Energy Sad Blues**
This was the most revealing normal-vs-adversarial comparison. The system chose genre and mood loyalty (5.0 pts) over energy accuracy and gave Worn-Out Shoes Blues the top spot despite its energy being 0.60 away from the target. The score (7.30/8.5) looks deceptively high — but the bar chart shows it only filled about 12 of 14 blocks because the energy penalty was large.

**Adversarial: Genre Not in Catalog (Reggae)**
When no song in the catalog matches the genre, the system silently loses 3 out of 8.5 points on every single song. The best result (Ember & Ash, 5.26/8.5) looks decent in isolation but actually represents a degraded experience — the ceiling dropped from 8.5 to 5.5 with no notification to the user. A real product would need to flag this.

**Adversarial: Metal Fan Who Wants Quiet Acoustic**
Iron Crown — the only metal/angry song — has energy 0.97 and acousticness 0.04, nearly the opposite of what this user asked for numerically. It still won at 5.66/8.5. This felt wrong when I saw it, because genre+mood weight is strong enough to override explicit numeric preferences entirely. The system answered "what genre do you like?" more than "what does this listening session feel like?"

## What the Weight Experiment Showed

Doubling the energy weight and halving the genre weight caused Rooftop Lights (indie pop / energy 0.76) to swap with Gym Hero (pop / energy 0.93) at ranks 2 and 3. The #1 song stayed the same, and so did #4 and #5. The change was narrow but meaningful: Gym Hero shares the pop genre with the user but has energy further from the target, while Rooftop Lights has different genre but nearly perfect energy. With the higher energy weight, closeness to the target mattered more than the genre label.

This confirmed that the weights are not neutral — they encode a design choice about what "a good recommendation" means. There is no objectively correct set of weights; it depends entirely on what you think users care about most.

## What I Learned

The biggest insight was that transparent scoring is both a strength and a limitation. Because every score is a simple weighted sum, I can always explain exactly why a song ranked where it did. But that same simplicity means the system cannot handle nuance — a user who wants "something like what I usually listen to but slightly different" has no way to express that.

I also learned that bias in a recommender is often invisible. The genre lock problem does not look like a bug from the output — it looks like the system is working. Only when you run many profiles and notice the same three songs keep appearing do you realize the weights are too lopsided. Real platforms have thousands of songs and millions of users, so this kind of structural bias could silently narrow what entire groups of people are exposed to — without anyone noticing.
