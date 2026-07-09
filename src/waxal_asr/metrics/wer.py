"""WER and CER computation.

Implemented directly (no external dependency) so behavior is fully controlled and
testable. Word-level and character-level edit distance computed via dynamic programming.
The combined score follows the challenge metric: `0.5 * WER + 0.5 * CER`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

__all__ = ["cer", "combined_score", "edit_distance", "wer"]


def edit_distance(ref: Sequence, hyp: Sequence) -> int:
    """Levenshtein edit distance between two sequences (words or characters)."""
    m, n = len(ref), len(hyp)
    if m == 0:
        return n
    if n == 0:
        return m
    prev = list(range(n + 1))
    cur = [0] * (n + 1)
    for i in range(1, m + 1):
        cur[0] = i
        ri = ref[i - 1]
        for j in range(1, n + 1):
            cost = 0 if ri == hyp[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev, cur = cur, prev
    return prev[n]


def _error_rate(refs: Sequence[Sequence], hyps: Sequence[Sequence]) -> tuple[int, int]:
    """Return (total_edits, total_units) for aligned reference/hypothesis sequences."""
    if len(refs) != len(hyps):
        raise ValueError(f"Mismatched reference/hypothesis lengths: {len(refs)} != {len(hyps)}")
    total_edits = 0
    total_units = 0
    for ref, hyp in zip(refs, hyps, strict=True):
        total_edits += edit_distance(ref, hyp)
        total_units += len(ref)
    return total_edits, total_units


def wer(references: Iterable[str], hypotheses: Iterable[str]) -> float:
    """Word Error Rate.

    Computed as total word-level edits / total reference words.
    Returns 0.0 if all references are empty.
    """
    ref_words = [r.split() for r in references]
    hyp_words = [h.split() for h in hypotheses]
    edits, units = _error_rate(ref_words, hyp_words)
    return edits / units if units > 0 else 0.0


def cer(references: Iterable[str], hypotheses: Iterable[str]) -> float:
    """Character Error Rate.

    Computed as total char-level edits / total reference characters.
    Returns 0.0 if all references are empty.
    """
    ref_chars = [list(r) for r in references]
    hyp_chars = [list(h) for h in hypotheses]
    edits, units = _error_rate(ref_chars, hyp_chars)
    return edits / units if units > 0 else 0.0


def combined_score(references: Iterable[str], hypotheses: Iterable[str]) -> float:
    """Combined competition metric: `0.5 * WER + 0.5 * CER` (lower is better)."""
    references = list(references)
    hypotheses = list(hypotheses)
    return 0.5 * wer(references, hypotheses) + 0.5 * cer(references, hypotheses)
