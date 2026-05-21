# Transition Matrix — Mathematical Methodology

This document describes the full pipeline used by `scripts/fit_transition_matrix.py` to produce the `data/transition_matrix.npy` file that powers chord generation at runtime.

---

## Overview

The goal is to learn a 7×7 row-stochastic matrix **P** where entry **P**[i, j] is the empirical probability of transitioning from scale degree *i* to scale degree *j* in real song choruses. At runtime this matrix is temperature-scaled and used to drive a first-order Markov chain over the seven major-scale degrees I–VII.

The pipeline runs in six main stages:

```
Stream Chordonomicon
    → Extract chorus instances per song
        → Infer key, map chords to degrees
            → Reduce to minimal repeating unit
                → Accumulate bigram counts
                    → Smooth + normalize → P_base
```

---

## Stage 1 — Corpus

**Source:** Chordonomicon (Kantarelis et al., arXiv:2410.22046, 2024) — 666,000 songs streamed from HuggingFace (`ailsntua/Chordonomicon`). Each row has a `chords` field containing a raw chord string with inline structural tags.

**Filtering:** Songs are skipped if:
- `chords` field is empty or absent
- No `<chorus_N>` tag is found anywhere in the chord string (see Stage 2)

Optional CLI filters (`--genre`, `--decade`) restrict to a genre substring or exact decade before corpus processing.

**Convergence monitoring:** Every 10,000 songs the current smoothed matrix is compared to its previous snapshot using the sup-norm:

```
Δ = max |P_current[i,j] - P_prev[i,j]|
```

The fitting run reports convergence status at each checkpoint (`converged` when Δ < 1×10⁻⁴).

---

## Stage 2 — Section extraction

**Why choruses only?**  
Verses and bridges are harmonically exploratory; choruses are the stable, repeated harmonic loop that defines a song's tonal center. Training on choruses produces a cleaner, more representative distribution of resolved harmonic motion.

**Tag format:** Chordonomicon encodes structure as inline tags: `<chorus_1>`, `<chorus_2>`, `<verse_1>`, etc. A song's chord string typically looks like:

```
<intro_1> C G <verse_1> Am F C G <chorus_1> F C G Am <chorus_2> F C G Am
```

**`extract_section_instances(chord_string, section)`** splits on each `<chorus_N>` boundary and returns *separate* token lists — one per numbered tag:

```python
parts = re.split(r'(<[^>]+>)', chord_string)
# Each time a new <chorus_N> tag is seen, a new list is started.
# Non-chorus tags flush the current list to results.
```

This is critical: a naïve approach that concatenates all chorus tokens produces artificial cross-boundary transitions (last chord of `<chorus_1>` → first chord of `<chorus_2>`) and inflates reported lengths by a factor equal to the number of repetitions.

---

## Stage 3 — Pitch-class notation

Chordonomicon uses a compact notation where sharps are written with `s`: `Cs` = C♯, `Fs` = F♯, etc. The 12 pitch classes are indexed 0–11:

| Index | 0 | 1  | 2 | 3  | 4 | 5 | 6  | 7 | 8  | 9 | 10 | 11 |
|-------|---|----|---|----|---|---|----|---|----|---|----|----|
| Name  | C | Cs | D | Ds | E | F | Fs | G | Gs | A | As | B  |

**`parse_chord_root(chord_str)`** extracts the pitch-class index from a chord token:

1. Strip slash-chord bass note: `A/Cs` → `A`
2. Match `^([A-G]s?)` to capture the root with optional sharp
3. Look up in `NOTE_TO_IDX`; return `None` for unrecognized tokens

Extensions (`maj7`, `min`, `add9`, etc.) and inversion slashes are ignored — only the root pitch class matters for degree inference.

---

## Stage 4 — Key inference

Each song's tonic is inferred independently from all its chorus tokens combined (pooling across `<chorus_1>`, `<chorus_2>`, … gives more signal than using just one instance).

**Algorithm (Temperley-style maximum diatonic coverage):**

The major scale starting on tonic *t* uses semitone offsets {0, 2, 4, 5, 7, 9, 11}. For each of the 12 candidate tonics:

```
score(t) = Σ count(r)  for all roots r whose pitch class is diatonic to t
```

The tonic with the highest score is selected. Ties are broken by the frequency of the tonic chord itself (i.e., how many times the root *t* appears). This tie-breaker biases toward major over relative minor, which is appropriate since the matrix is built over major-mode scale degrees.

Songs for which no chord roots can be parsed at all are skipped (return `(0, 0)` from `accumulate_song`).

---

## Stage 5 — Degree mapping

**`chord_to_degree(root_idx, key_idx)`** maps a pitch-class index to a scale degree 0–6:

```
interval = (root_idx - key_idx) mod 12
```

If `interval` is one of {0, 2, 4, 5, 7, 9, 11} (the major scale offsets), the function returns its position in that list (0=I, 1=II, …, 6=VII). Chromatic roots (not in the scale) return `None` and are **not** added to the degree sequence — they are counted separately as chromatic chords but do not contribute bigrams to the transition matrix.

**Consecutive-root deduplication:** Before degree mapping, consecutive identical roots are collapsed:

```python
if root is None or root == prev_root:
    continue
```

This prevents a chord held across a bar line (e.g., `C C C G`) from producing false self-loops in the matrix.

---

## Stage 6 — Minimal repeating unit

After mapping a chorus instance to a degree sequence, the sequence is reduced to its shortest tiling prefix before bigrams are counted.

**`minimal_repeating_unit(seq)`** — linear scan over candidate periods:

```python
for p in range(1, n):
    if all(seq[i] == seq[i % p] for i in range(n)):
        return list(seq[:p])
return list(seq)
```

This handles two cases:
- **Exact repetition:** `[I, IV, V, I, IV, V]` → `[I, IV, V]`
- **Partial trailing repetition:** `[I, IV, V, I, IV]` → `[I, IV, V]`

Without this step, a single `<chorus_1>` tag containing the same 4-chord loop written out twice would contribute 7 bigrams (and report length 8) instead of the correct 3 bigrams (length 4). Across hundreds of thousands of songs this matters significantly for both the bigram counts and the length distribution.

---

## Stage 7 — Bigram accumulation

**`accumulate_song`** orchestrates Stages 2–6 for one song and writes directly into a shared `(7, 7)` count matrix:

```
For each chorus instance:
    1. Parse roots, deduplicate consecutives
    2. Map diatonic roots to degrees (skip chromatics)
    3. minimal_repeating_unit(degrees)
    4. For i in 0..len-2: count_matrix[degrees[i], degrees[i+1]] += 1
```

Key design decisions:
- **No cross-instance transitions:** Each chorus instance is processed independently. The last degree of `<chorus_1>` never produces a bigram with the first degree of `<chorus_2>`.
- **Key inferred from all instances combined:** The key assignment is stable across repetitions (more data = more reliable inference), but bigrams are accumulated per-instance after applying `minimal_repeating_unit` to each.
- **Length = first instance only:** The returned `first_length` is the degree-count of `chorus_1` after deduplication and MRU reduction. Later repetitions are (by definition) the same loop and should not inflate the length distribution.

---

## Stage 8 — Laplace (add-α) smoothing

After streaming the full corpus, the raw count matrix has cells that may be zero (some degree-to-degree transitions simply never occur in the data). Zero entries cause numerical problems during temperature scaling (log(0) = −∞).

Laplace smoothing adds a pseudo-count α to every cell before normalizing:

```
smoothed[i, j] = count_matrix[i, j] + α
```

The default is **α = 1.0** (add-one smoothing), configurable via `--alpha`. This is a relatively weak prior — with ~millions of bigrams in the corpus the smoothing has a negligible effect on high-frequency transitions and only affects the near-zero cells.

---

## Stage 9 — Row normalization

The smoothed count matrix is converted to a row-stochastic probability matrix by dividing each row by its sum:

```
P_base[i, j] = smoothed[i, j] / Σ_k smoothed[i, k]
```

The result **P_base** is a (7, 7) float64 matrix where every row sums to 1. This is serialized to `data/transition_matrix.npy`.

---

## Stage 10 — Chorus length distribution

Alongside the matrix, the first-instance chorus lengths are collected into a `Counter[int]` capped at 32. After fitting:

```python
raw = [length_counts.get(i, 0) for i in range(1, max_observed + 1)]
length_dist = raw / raw.sum()          # normalized to probability
```

This 1-D array is saved to `data/transition_matrix_lengths.npy`. Index *k* holds P(length = k+1). At generation time the array is **truncated** to `_MAX_GENERATION_LENGTH = 7` and renormalized, so progressions longer than 7 chords are never generated.

---

## At runtime — Temperature scaling

`strategy.py` loads P_base as a log-weight matrix. Given a temperature τ > 0, the generation matrix is:

```
P(τ)[i, j] = softmax( log(P_base[i, j]) / τ )_j
```

Implemented as numerically stable row-wise softmax:

```python
W = log(P_base) / tau          # log-weight matrix scaled by τ
W_s = W - W.max(axis=1)        # subtract row max for numerical stability
P = exp(W_s) / exp(W_s).sum(axis=1)
```

Two presets ship with the tool:

| Mode      | τ   | Effect                                             |
|-----------|-----|----------------------------------------------------|
| Relaxed   | 0.5 | Sharpens distribution; familiar voice-leading      |
| Challenge | 2.5 | Flattens toward uniform; chromatic, unpredictable  |

τ = 1 recovers P_base exactly. As τ → 0 the chain becomes deterministic (always follows the highest-probability transition). As τ → ∞ all transitions become equally likely.

---

## At runtime — Entropy rate

The Shannon entropy rate **H** of the scaled chain quantifies how many bits of harmonic information are generated per chord step. It is computed from the stationary distribution π (found by power iteration) and the transition matrix P(τ):

```
π^(t+1) = π^(t) · P(τ)          (until max |Δπ| < 1×10⁻¹⁰)

H = − Σ_i π_i · Σ_j P[i,j] · log₂(P[i,j])    (bits/chord)
```

The maximum possible entropy is log₂(7) ≈ 2.807 bits (achieved by a uniform 7×7 matrix). H is printed on every generated card as a quantitative difficulty signal:

| Mode      | τ   | H (approx.) | % of max |
|-----------|-----|-------------|----------|
| Relaxed   | 0.5 | ~1.0 bits   | ~36%     |
| Challenge | 2.5 | ~2.7 bits   | ~96%     |

---

## Notation reference

| Symbol      | Meaning                                              |
|-------------|------------------------------------------------------|
| **P_base**  | Corpus-fitted row-stochastic (7×7) matrix at τ=1     |
| **P(τ)**    | Temperature-scaled generation matrix                 |
| τ           | Temperature; controls sharpness of transitions       |
| α           | Laplace smoothing pseudo-count (default 1.0)         |
| **π**       | Stationary distribution of P(τ) under power iteration|
| H           | Shannon entropy rate (bits per chord)                |
| MRU         | Minimal repeating unit of a degree sequence          |
| I–VII       | Diatonic scale degrees (0-indexed: 0=I, …, 6=VII)   |

---

*Corpus reference: Kantarelis et al., "CHORDONOMICON: A Dataset of 666,000 Songs and their Chord Progressions", arXiv:2410.22046, 2024.*
