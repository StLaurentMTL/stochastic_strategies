# Chordonomicon Notebook — Dataset Insights

This document summarizes the findings from `notebooks/explore_chordonomicon.ipynb`, which explores a 5,000-song streaming sample of the Chordonomicon dataset to validate the assumptions behind the transition matrix fitting pipeline and characterize how pop harmony has changed across decades.

---

## Dataset overview

Chordonomicon ships 10 columns per song:

| Column              | Type    | Null rate (sample) |
|---------------------|---------|--------------------|
| `id`                | int64   | 0%                 |
| `chords`            | object  | 0%                 |
| `release_date`      | object  | 24%                |
| `genres`            | object  | 33%                |
| `decade`            | float64 | 24%                |
| `rock_genre`        | object  | 82%                |
| `artist_id`         | object  | 11%                |
| `main_genre`        | object  | 47%                |
| `spotify_song_id`   | object  | 22%                |
| `spotify_artist_id` | object  | 11%                |

Key observations:
- `chords` is always present — the fitting script never needs to handle missing chord strings.
- Nearly half of songs lack a `main_genre` label, which is why `--genre` filtering discards a large fraction of the corpus when used.
- `decade` is missing for ~24% of songs (mostly older catalog where release metadata is unavailable).

---

## Genre distribution

In the 5,000-song sample the genre field is highly fragmented — the dataset aggregates tags from multiple sources and many songs have several. The top `main_genre` values by count are roughly: **pop**, **metal**, **rock**, **hip-hop/rap**, **country**, with pop and metal together accounting for the majority of labeled songs.

**Implication for the default matrix:** The default fit runs over all genres, so the resulting transition matrix reflects a genre-mixed population. Single-genre fits (e.g., `--genre pop`) produce a sharper, more idiomatically consistent matrix at the cost of reduced corpus size.

---

## Decade distribution

Songs cluster heavily in the 2010s and 2020s — the dataset has better coverage of recent music than older decades. The 1930s–1950s have very few entries (under ~20 songs in the sample). Decade-filtered fits on pre-1970 music are therefore unreliable due to small sample sizes and should be treated as illustrative only.

---

## Section types

The notebook counts how many songs contain each structural section type (stripping the numeric suffix so `chorus_1` and `chorus_2` both count as `chorus`). The most common sections in descending frequency are:

1. **chorus** — present in the large majority of songs
2. **verse**
3. **bridge**
4. **intro**
5. **outro**
6. **pre-chorus**, **interlude**, **solo** (sparse)

The dominance of `chorus` tags confirms that the chorus-only filtering strategy retains the bulk of songs rather than discarding most of the corpus. Songs without a chorus tag — a distinct minority — are skipped entirely by the fitting script.

---

## Chorus progression length distribution

This is the most directly consequential analysis for the generator. The notebook measures the **minimal repeating unit length** of each song's first chorus instance — the number of unique diatonic degrees in the shortest chord loop before it begins repeating.

Key statistics from the 5,000-song sample:

- **Mode: 4 chords.** The I–V–vi–IV and similar 4-chord loops dominate.
- **Median: 4 chords.**
- The distribution is right-skewed: the vast majority of choruses fall between 3 and 6 unique chords, with a long tail extending to 8–12 for more harmonically complex songs.
- Lengths above ~12 are rare and typically indicate songs where the "chorus" tag encompasses a large non-repeating section or where key inference mis-fires.

The `data/transition_matrix_lengths.npy` file captures this full distribution over the complete corpus. At runtime, the distribution is **truncated at 7** and renormalized, so progressions longer than 7 chords are never generated — the truncation captures over 95% of the empirical probability mass, meaning generated progressions are representative of real chorus loops.

---

## Most common chord roots

Across all sections, **C** and **G** are the most frequent chord roots by a significant margin, followed by **F**, **Am** (root A), **D**, and **E**. This reflects the strong bias in the dataset toward guitar-friendly keys (C major, G major, D major).

**Implication:** A key-agnostic root-frequency analysis would suggest C-heavy harmony, but the transition matrix is computed in *relative scale degrees* after key normalization, so the absolute pitch distribution does not bias the generated progressions. The generator then maps degrees back to a randomly chosen key, giving uniform key coverage.

---

## Inferred key distribution

Using the Temperley maximum-diatonic-coverage key inference, the most frequently inferred keys in the sample are **C**, **G**, **D**, **A**, and **E** — the five sharp-side keys accessible with open guitar chords. Flat keys (F, Bb, Eb) appear less often.

This is a corpus artifact (guitar-centric songwriting) rather than a limitation of the inference algorithm. The transition matrix is key-agnostic (built over relative degrees I–VII), so this distribution does not affect the quality of generated progressions.

**Chord root frequency by key (heatmap):** The notebook includes a row-normalized heatmap of which roots appear within each inferred key. The diagonal (tonic chord) is consistently the most frequent root within its key, confirming that the Temperley inference is well-calibrated. The secondary peaks fall on the V and IV degrees — standard pop/rock voice-leading.

---

## Pop harmony across the decades

The most analytically rich section of the notebook streams up to 8,000 pop songs, groups them by decade, and builds a separate 7×7 transition matrix per decade. Three metrics are tracked:

### Entropy rate H (bits/chord)

The entropy rate measures how unpredictable chord transitions are within a decade's pop corpus. Higher entropy = more varied, less formulaic progressions.

**Trend:** Entropy is highest in the 1960s–1970s, dips noticeably in the 1980s–1990s (the era of maximally formulaic four-chord pop), then rises moderately from the 2000s onward as genre hybridity and hip-hop-influenced pop introduce less conventional harmonic motion.

The absolute values stay below 2.0 bits/chord for all decades, well short of the theoretical maximum of log₂(7) ≈ 2.81 bits — pop harmony is never truly random.

### Diatonic ratio (% of chorus chords in key)

The fraction of chords that are diatonic to the inferred key measures how "in-key" pop choruses are.

**Trend:** Diatonic ratio is consistently high (80–90%+) across all decades, validating the design decision to treat the transition matrix as a diatonic-degree model and insert chromatic chords separately via the `p_chromatic` parameter. Pop choruses are overwhelmingly diatonic.

The ratio is slightly lower in the 1960s–1970s (more jazz-influenced passing chords and borrowed chords) and again in the 2010s–2020s (hip-hop-influenced trap-pop using more chromatic passing tones).

### Mean chorus length (diatonic chords)

**Trend:** Mean length is stable across decades, hovering around 4–5 diatonic degrees per chorus. This cross-decade stability justifies using a single pooled length distribution rather than decade-specific distributions at runtime. The standard deviation within each decade is larger than the decade-to-decade variation in the mean.

### Per-decade transition matrices

The notebook renders small-multiple 7×7 heatmaps — one per decade — on a shared color scale so cells are directly comparable. Notable observations:

- **I→V** and **V→I** are the dominant transitions in every decade, as expected from tonal gravity.
- **vi→IV** and **IV→I** are consistently strong secondary transitions (the backbone of the I–V–vi–IV loop).
- **II→V** appears prominently in the 1960s–1970s (jazz-influenced secondary dominants) and weakens in later decades.
- **VII→I** (leading-tone resolution) is present but weaker than V→I across all decades, reflecting that VII chords are less common in pop than classical contexts.
- The matrices become slightly more uniform (higher entropy) in the 1960s and again in the 2020s, consistent with the entropy rate trends.

### Most variable transitions across decades

The 12 bigrams with the highest cross-decade variance (ranked by variance of their probability across the decade matrices) reveal which harmonic moves have shifted most in pop history:

- **II→V** shows the largest decline from the 1960s to the 2000s — the classic jazz cadential move fades in modern pop.
- **vi→I** and **vi→IV** both show increasing variance in the 2010s–2020s, reflecting the growing use of vi as a tonic substitute.
- Self-loops (I→I, IV→IV) have low variance but nonzero probability across all decades — these appear when the chord parser catches notation artifacts rather than genuine voice-leading.
- Several transitions involving **III** and **VII** are among the most variable, as these degrees appear inconsistently across genres and decades.

---

## Takeaways for the generator

| Finding | Generator implication |
|---|---|
| Mode chorus length = 4, 95%+ ≤ 7 | `_MAX_GENERATION_LENGTH = 7` captures nearly all real chorus loops |
| Diatonic ratio consistently >80% | Chromatic insertions are a valid but minority operation; `p_chromatic` should stay low |
| Entropy well below log₂(7) for all decades | The corpus matrix is genuinely informative (not uniform noise) |
| I→V and V→I dominate every decade | The music-theory prior in `_W_PRIOR` correctly encodes the strongest transitions |
| II→V declining across decades | Genre-filtered fits (e.g., `--genre pop --decade 2010`) can tune toward contemporary idioms |
| Length distribution stable across decades | A single pooled length file is an appropriate default |

---

*Corpus reference: Kantarelis et al., "CHORDONOMICON: A Dataset of 666,000 Songs and their Chord Progressions", arXiv:2410.22046, 2024.*
