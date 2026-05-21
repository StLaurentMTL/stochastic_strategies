"""
fit_transition_matrix.py
========================
Offline fitting script for the Stochastic Strategies transition matrix.

Run this once locally to produce `transition_matrix.npy`, which is then
committed to the repository and loaded at runtime by strategy.py.

Requires:
    pip install datasets numpy

Usage:
    python fit_transition_matrix.py [--genre pop] [--decade 2010] [--out transition_matrix.npy]

Pipeline:
    1. Stream Chordonomicon from HuggingFace (ailsntua/Chordonomicon)
    2. For each song, extract chords from chorus sections only.
       extract_section_instances splits on each <chorus_N> tag boundary so
       that each repetition is an independent token list — no cross-boundary
       transitions, no inflated lengths from back-to-back choruses.
       Songs with no chorus tag are skipped entirely.
    3. Apply minimal_repeating_unit to each chorus instance before counting.
       A 4-chord loop played twice inside a single chorus tag is counted as
       4 chords, not 8, and contributes only one copy of the bigrams.
    4. Infer key via maximum diatonic coverage (Temperley-style) over all
       chorus instances combined; accumulate bigram counts over the 7 major
       scale degrees (I-VII). Only the first instance's length is recorded.
    5. Apply Laplace smoothing (add-alpha) and row-normalize to produce P_base.
    6. Serialize as (7, 7) float64 numpy array. A companion _lengths.npy
       stores the empirical chorus-loop-length distribution (1-indexed).

The resulting matrix encodes empirical transition probabilities over relative
scale degrees I-VII. At runtime, temperature scaling is applied:

    P(tau)_ij = softmax(log(P_base_ij) / tau)_j

so P_base corresponds to tau=1. Relaxed mode uses tau < 1 (sharpens toward
most probable transitions); Challenge mode uses tau > 1 (flattens toward uniform).

Citation:
    Kantarelis et al., "CHORDONOMICON: A Dataset of 666,000 Songs and their
    Chord Progressions", arXiv:2410.22046, 2024.
"""

import re
import argparse
from pathlib import Path

import numpy as np
from collections import Counter

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_DIR.mkdir(exist_ok=True)

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

_MAX_PROG_LEN = 32        # cap for the length distribution histogram
_CONV_CHECK_EVERY = 10_000  # songs between convergence snapshots
_CONV_TOL = 1e-4            # sup-norm threshold to declare convergence
_DEGREE_NAMES = ["I", "II", "III", "IV", "V", "VI", "VII"]

# ---------------------------------------------------------------------------
# Pitch-class constants
# Chordonomicon uses 's' for sharps: Cs=C#, Fs=F#, Gs=G#, As=A#, Ds=D#
# ---------------------------------------------------------------------------
NOTES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]
NOTE_TO_IDX = {n: i for i, n in enumerate(NOTES)}
MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]   # semitone offsets of major scale degrees I–VII


# ---------------------------------------------------------------------------
# Chord parsing
# ---------------------------------------------------------------------------

def parse_chord_root(chord_str: str) -> int | None:
    """
    Extract pitch-class index (0–11) from a chord token.
    Handles: slash chords (A/Cs -> A), extensions (Dmaj7 -> D), accidentals.
    Returns None if the token is not a recognizable chord.
    """
    chord_str = chord_str.split("/")[0]
    m = re.match(r'^([A-G]s?)', chord_str)
    if not m:
        return None
    return NOTE_TO_IDX.get(m.group(1))


def strip_structural_tags(chord_string: str) -> list[str]:
    """Remove <tag> markers and return list of chord tokens."""
    cleaned = re.sub(r'<[^>]+>', ' ', chord_string)
    return [t for t in cleaned.split() if t]


# ---------------------------------------------------------------------------
# Key inference: maximum diatonic coverage
# ---------------------------------------------------------------------------

def infer_key(chord_tokens: list[str]) -> int | None:
    """
    Infer the tonic pitch-class index by finding the key that maximizes
    the count of diatonic chord occurrences (Temperley-style coverage).

    Ties are broken by frequency of the tonic chord itself, which slightly
    biases toward major over relative minor (desired, since we build a
    major-mode transition matrix).

    Returns None if no chord roots can be parsed.
    """
    roots = [parse_chord_root(t) for t in chord_tokens]
    roots = [r for r in roots if r is not None]
    if not roots:
        return None

    root_counts = Counter(roots)
    best_key: int | None = None
    best_score: int = -1
    best_tonic_freq: int = -1

    for tonic in range(12):
        diatonic_set = {(tonic + d) % 12 for d in MAJOR_INTERVALS}
        score = sum(cnt for r, cnt in root_counts.items() if r in diatonic_set)
        tonic_freq = root_counts.get(tonic, 0)
        if score > best_score or (score == best_score and tonic_freq > best_tonic_freq):
            best_score = score
            best_tonic_freq = tonic_freq
            best_key = tonic

    return best_key


def chord_to_degree(root_idx: int, key_idx: int) -> int | None:
    """
    Map a pitch-class index to scale degree 0–6 given a tonic.
    Returns None for chromatic (non-diatonic) chords.
    """
    interval = (root_idx - key_idx) % 12
    if interval in MAJOR_INTERVALS:
        return MAJOR_INTERVALS.index(interval)
    return None


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------

def extract_section(chord_string: str, section: str | None) -> list[str]:
    """
    Extract chord tokens from a specific structural section of a song.

    Chordonomicon encodes sections as tags like <chorus_1>, <verse_2>, etc.
    If section is None, all tokens from the entire song are returned.
    If the requested section is not present, returns [] (song is skipped).

    NOTE: This concatenates all matching instances (chorus_1, chorus_2, …).
    For per-instance splitting use extract_section_instances().

    Parameters
    ----------
    chord_string : raw chord string from the dataset
    section      : 'chorus', 'verse', 'bridge', 'intro', 'outro', or None
    """
    if section is None:
        return strip_structural_tags(chord_string)

    parts = re.split(r'(<[^>]+>)', chord_string)
    tokens = []
    in_target = False
    for part in parts:
        if part.startswith('<'):
            tag_name = part.strip('<>').lower()
            in_target = tag_name.startswith(section.lower())
        elif in_target:
            tokens.extend(t for t in part.split() if t)
    return tokens


def extract_section_instances(chord_string: str, section: str) -> list[list[str]]:
    """
    Extract each numbered instance of `section` as a separate token list.

    Unlike extract_section, each <section_N> tag boundary starts a fresh list,
    so <chorus_1> … <chorus_2> … yields two independent lists instead of one
    concatenated blob. Songs with no matching tags return [].

    This is the correct granularity for measuring how long a single chorus
    loop is — repeated choruses with the same chords should not inflate length.
    """
    parts = re.split(r'(<[^>]+>)', chord_string)
    instances: list[list[str]] = []
    current: list[str] | None = None

    for part in parts:
        if part.startswith('<'):
            tag = part.strip('<>').lower()
            if tag.startswith(section.lower()):
                if current is not None:
                    instances.append(current)
                current = []
            else:
                if current is not None:
                    instances.append(current)
                    current = None
        elif current is not None:
            current.extend(t for t in part.split() if t)

    if current is not None:
        instances.append(current)

    return [inst for inst in instances if inst]


def minimal_repeating_unit[T](seq: list[T]) -> list[T]:
    """
    Return the shortest prefix of `seq` that tiles the whole sequence.

    Handles both exact repetitions (A-B-C-A-B-C → A-B-C) and partial
    trailing repetitions (A-B-C-A-B → A-B-C), so a chorus with the
    same 4-chord loop played 2.5 times is counted as 4 chords, not 10.
    """
    n = len(seq)
    for p in range(1, n):
        if all(seq[i] == seq[i % p] for i in range(n)):
            return list(seq[:p])
    return list(seq)


# ---------------------------------------------------------------------------
# Count matrix accumulation
# ---------------------------------------------------------------------------

def accumulate_song(chord_string: str, count_matrix: np.ndarray,
                    section: str | None = None) -> tuple[int, int]:
    """
    Parse one song, infer key, and accumulate diatonic bigram counts into
    count_matrix[from_degree, to_degree].

    When `section` is given, each tagged instance (e.g. chorus_1, chorus_2)
    is processed independently — bigrams are never counted across instance
    boundaries, and the returned length is that of the FIRST instance only
    (the best proxy for a single chorus loop; later repetitions are the same
    pattern and should not inflate the length distribution).

    Songs that have no tag matching `section` return (0, 0) and are skipped.
    Consecutive repeated chord roots are collapsed before counting.

    Returns (bigrams_added, first_instance_length). Both 0 if skipped.
    """
    if section is None:
        tokens = strip_structural_tags(chord_string)
        instances = [tokens] if tokens else []
    else:
        instances = extract_section_instances(chord_string, section)

    if not instances:
        return 0, 0

    all_tokens = [t for inst in instances for t in inst]
    key = infer_key(all_tokens)
    if key is None:
        return 0, 0

    total_added = 0
    first_length = 0

    for idx, inst_tokens in enumerate(instances):
        degrees: list[int] = []
        prev_root: int | None = None
        for t in inst_tokens:
            root = parse_chord_root(t)
            if root is None or root == prev_root:
                continue
            deg = chord_to_degree(root, key)
            if deg is not None:
                degrees.append(deg)
            prev_root = root

        degrees = minimal_repeating_unit(degrees)

        for i in range(len(degrees) - 1):
            count_matrix[degrees[i], degrees[i + 1]] += 1
            total_added += 1

        if idx == 0:
            first_length = len(degrees)

    return total_added, first_length


# ---------------------------------------------------------------------------
# Matrix visualization
# ---------------------------------------------------------------------------

def plot_matrix(P: np.ndarray, out_path: str | None = None) -> None:
    """Colored heatmap of the learned (7×7) transition matrix."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install matplotlib to visualize: pip install matplotlib")
        return

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(P, cmap="YlOrRd", vmin=0, vmax=P.max())

    ax.set_xticks(range(7))
    ax.set_yticks(range(7))
    ax.set_xticklabels(_DEGREE_NAMES, fontsize=13, fontweight="bold")
    ax.set_yticklabels(_DEGREE_NAMES, fontsize=13, fontweight="bold")
    ax.set_xlabel("To", fontsize=13, labelpad=8)
    ax.set_ylabel("From", fontsize=13, labelpad=8)
    ax.set_title("Chordonomicon — Transition Matrix  (τ = 1)", fontsize=14, pad=14)

    threshold = P.max() * 0.55
    for i in range(7):
        for j in range(7):
            color = "white" if P[i, j] >= threshold else "black"
            ax.text(j, i, f"{P[i, j]:.3f}", ha="center", va="center",
                    fontsize=9.5, color=color, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Transition probability", fontsize=11)
    plt.tight_layout()

    if out_path:
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        print(f"Saved matrix plot to {out_path}")
    plt.show()


# ---------------------------------------------------------------------------
# Main fitting routine
# ---------------------------------------------------------------------------

def fit(genre_filter: str | None = None,
        decade_filter: int | None = None,
        alpha: float = 1.0,
        max_songs: int | None = None,
        out_path: Path = _DATA_DIR / "transition_matrix.npy",
        plot: bool = True) -> np.ndarray:
    """
    Stream Chordonomicon, accumulate chorus bigrams, and save the smoothed
    row-stochastic transition matrix.

    Parameters
    ----------
    genre_filter : str or None
        Filter to songs whose main_genre matches (e.g. 'pop', 'rock').
    decade_filter : int or None
        Filter to songs from this decade (e.g. 2010).
    alpha : float
        Laplace (add-alpha) smoothing parameter.
    max_songs : int or None
        Cap on songs processed (useful for quick tests).
    out_path : str
        Path for the (7, 7) float64 .npy output.
    plot : bool
        If True, display a colored heatmap of the fitted matrix.

    Returns
    -------
    P : np.ndarray, shape (7, 7)
    """
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("Install the 'datasets' package: pip install datasets")

    console = Console()
    console.print("[bold]Loading Chordonomicon[/bold] (streaming from HuggingFace)…")
    ds = load_dataset("ailsntua/Chordonomicon", split="train", streaming=True)

    count_matrix = np.zeros((7, 7), dtype=np.float64)
    length_counts: Counter[int] = Counter()
    n_songs = 0
    n_bigrams = 0
    n_skipped = 0

    P_prev: np.ndarray | None = None
    conv_log: list[tuple[int, float]] = []
    last_delta = "—"

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        TextColumn("  [green]{task.fields[songs]:>8,}[/] songs"),
        TextColumn("  [cyan]{task.fields[bigrams]:>10,}[/] bigrams"),
        TextColumn("  [yellow]Δ={task.fields[delta]}[/]"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task(
            "Streaming", total=None, songs=0, bigrams=0, delta=last_delta,
        )

        for row in ds:
            if max_songs is not None and n_songs >= max_songs:
                break

            # Optional filters
            if genre_filter is not None:
                mg = (row.get("main_genre") or "").lower()
                if genre_filter.lower() not in mg:
                    n_skipped += 1
                    continue

            if decade_filter is not None:
                dec = row.get("decade")
                if dec is None or int(dec) != decade_filter:
                    n_skipped += 1
                    continue

            chord_string = row.get("chords") or ""
            if not chord_string.strip():
                n_skipped += 1
                continue

            added, prog_len = accumulate_song(chord_string, count_matrix, section="chorus")
            n_bigrams += added
            if prog_len >= 1:
                length_counts[min(prog_len, _MAX_PROG_LEN)] += 1
            n_songs += 1

            # Refresh display every 500 songs
            if n_songs % 500 == 0:
                progress.update(task, songs=n_songs, bigrams=n_bigrams, delta=last_delta)

            # Convergence check every _CONV_CHECK_EVERY songs
            if n_songs % _CONV_CHECK_EVERY == 0:
                sm = count_matrix + alpha
                P_check = sm / sm.sum(axis=1, keepdims=True)
                if P_prev is not None:
                    delta = float(np.max(np.abs(P_check - P_prev)))
                    conv_log.append((n_songs, delta))
                    last_delta = f"{delta:.2e}"
                    progress.update(task, delta=last_delta)
                P_prev = P_check.copy()

        progress.update(task, songs=n_songs, bigrams=n_bigrams,
                        delta=last_delta, description="Complete")

    # ── Summary ──────────────────────────────────────────────────────────────
    summary = Table(title="Fitting summary  (chorus sections)", show_header=False)
    summary.add_column(justify="right", style="bold")
    summary.add_column()
    summary.add_row("Songs processed", f"{n_songs:,}")
    summary.add_row("Songs skipped",   f"{n_skipped:,}")
    summary.add_row("Diatonic bigrams", f"{n_bigrams:,}")
    summary.add_row("Diatonic rate",
                    f"{n_bigrams / max(n_bigrams + n_skipped, 1):.1%}")
    console.print(summary)

    # ── Convergence log ───────────────────────────────────────────────────────
    if conv_log:
        conv_table = Table(title="Convergence  (sup-norm ΔP per 10 k songs)")
        conv_table.add_column("Songs", justify="right")
        conv_table.add_column("max |ΔP|", justify="right")
        conv_table.add_column("Status")
        for ck_songs, delta in conv_log:
            if delta < _CONV_TOL:
                status = "[bold green]converged[/]"
            elif delta < _CONV_TOL * 10:
                status = "[yellow]nearly there[/]"
            else:
                status = "[red]changing[/]"
            conv_table.add_row(f"{ck_songs:,}", f"{delta:.4e}", status)
        console.print(conv_table)

    # ── Laplace smoothing + row normalization ─────────────────────────────────
    smoothed = count_matrix + alpha
    P = smoothed / smoothed.sum(axis=1, keepdims=True)

    # ── Terminal matrix table (color-coded) ───────────────────────────────────
    mat_table = Table(title="Transition matrix  P(τ=1)")
    mat_table.add_column("", style="bold")
    for d in _DEGREE_NAMES:
        mat_table.add_column(d, justify="right")

    p_max = P.max()
    for i, row_p in enumerate(P):
        cells = []
        for v in row_p:
            ratio = v / p_max
            if ratio > 0.6:
                cells.append(f"[bold red]{v:.3f}[/]")
            elif ratio > 0.35:
                cells.append(f"[yellow]{v:.3f}[/]")
            else:
                cells.append(f"[dim]{v:.3f}[/]")
        mat_table.add_row(_DEGREE_NAMES[i], *cells)
    console.print(mat_table)

    # ── Save ──────────────────────────────────────────────────────────────────
    np.save(out_path, P)
    console.print(f"[bold green]Saved[/] transition matrix → [cyan]{out_path}[/]")

    if length_counts:
        max_observed = max(length_counts.keys())
        raw = np.array([length_counts.get(i, 0) for i in range(1, max_observed + 1)],
                       dtype=np.float64)
        length_dist = raw / raw.sum()
        len_path = out_path.with_name(out_path.stem + "_lengths.npy")
        np.save(len_path, length_dist)
        mode = int(np.argmax(length_dist)) + 1
        console.print(
            f"[bold green]Saved[/] length distribution "
            f"(1–{max_observed} chords, mode={mode}) → [cyan]{len_path}[/]"
        )

    # ── Heatmap ───────────────────────────────────────────────────────────────
    if plot:
        plot_path = str(out_path.with_name(out_path.stem + "_heatmap.png"))
        plot_matrix(P, out_path=plot_path)

    return P


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fit Markov transition matrix from Chordonomicon.")
    parser.add_argument("--genre", default=None,
                        help="Filter by main_genre (e.g. 'pop', 'rock'). Default: all genres.")
    parser.add_argument("--decade", type=int, default=None,
                        help="Filter by decade (e.g. 2010). Default: all decades.")
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="Laplace smoothing parameter (default: 1.0).")
    parser.add_argument("--max-songs", type=int, default=None,
                        help="Cap on songs to process (for quick tests).")
    parser.add_argument("--out", default=str(_DATA_DIR / "transition_matrix.npy"),
                        help=f"Output path for .npy file (default: {_DATA_DIR / 'transition_matrix.npy'}).")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip the matplotlib heatmap.")
    args = parser.parse_args()

    fit(genre_filter=args.genre,
        decade_filter=args.decade,
        alpha=args.alpha,
        max_songs=args.max_songs,
        out_path=Path(args.out),
        plot=not args.no_plot)
