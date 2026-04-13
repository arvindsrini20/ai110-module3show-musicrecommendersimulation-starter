# Reflection: Music Recommender Simulation

## What I Built

I built a content-based music recommender that scores every song in a 20-song catalog and returns the top 5 matches for a given user. The score is based on four things: genre match, mood match, energy closeness, and acoustic texture. Genre has the most weight because it is the strongest indicator of what someone wants to hear.

## Profile Comparisons

**High-Energy Pop vs. Chill Lofi Study**
Both profiles got near-perfect top scores (8.46/8.5) for songs that matched on all four features. The difference showed up lower in the rankings. The pop profile's 4th place was a synthwave/moody song because there were no more pop songs left. The lofi profile's 4th place was ambient/chill, which matched the mood but not the genre. This showed how genre lock works in practice: only 3 of the 20 songs are lofi, so the top 3 results are almost always the same titles no matter what.

**Deep Intense Rock**
Storm Runner scored 8.48/8.5, the highest score I saw across all tests. This one felt right. The genre, mood, and energy all lined up. The second place song (Gym Hero) was pop/intense, which shows that mood alone can move a song pretty high even without a genre match.

**Adversarial: High-Energy Sad Blues**
This was the most interesting one to look at. The user wanted sad blues music at a high energy of 0.90, but the only blues/sad song in the catalog has an energy of 0.30. The system still ranked it first with a score of 7.30/8.5. Genre and mood were worth 5.0 points combined, which was enough to beat out the energy penalty. The system prioritized the genre and mood match over the energy request, which is not always what a user actually wants.

**Adversarial: Genre Not in Catalog (Reggae)**
When no song in the catalog matches the genre, the system loses 3 points on every single comparison. The best result was Ember and Ash at 5.26/8.5, which looks okay but is actually the ceiling for this profile. The system does not notify the user that their genre is missing. It just quietly gives lower scores across the board.

**Adversarial: Metal Fan Who Wants Quiet Acoustic**
Iron Crown is the only metal/angry song in the catalog. It has energy 0.97 and acousticness 0.04, which is basically the opposite of what this user asked for. It still came in first at 5.66/8.5 because the genre and mood points (5.0 total) outweighed everything else. The system answered "what is your genre?" more than "what do you actually want this session to feel like?"

## What the Weight Experiment Showed

I doubled the energy weight from 2.0 to 4.0 and cut the genre weight from 3.0 to 1.5. The only change in the top 5 was that Rooftop Lights and Gym Hero swapped positions at ranks 2 and 3. Rooftop Lights has energy 0.76 (very close to the 0.80 target) while Gym Hero has energy 0.93 (further away). With the higher energy weight, being close to the target mattered more than sharing the same genre.

This showed me that the weights are not neutral. They decide what the system thinks is more important. There is no single correct answer, it just depends on what you want to prioritize.

## What I Learned

The biggest thing I learned is that a system can be working correctly and still give a result that feels wrong. The metal profile is the best example. The math was right, but the answer did not match what the user described. That made me realize that choosing the weights is just as important as writing the code.

I also learned that bias in a recommender is hard to spot just by looking at one result. The genre lock problem looks like the system is doing its job. You only notice it when you run the same profile multiple times and see the same songs showing up every time. In a real app with millions of users, that kind of pattern could quietly limit what people are exposed to without anyone realizing it.
