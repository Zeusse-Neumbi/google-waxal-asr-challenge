"""Text normalization for ASR evaluation.

Normalization must be applied identically to references and hypotheses before computing
WER/CER. All toggles are configurable via `configs/evaluation.yaml`.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from typing import Literal, cast

__all__ = ["normalize_corpus", "normalize_text"]

_WHITESPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_text(
    text: str,
    *,
    lowercase: bool = True,
    strip_punctuation: bool = True,
    unicode_normalization: str = "NFC",
    collapse_whitespace: bool = True,
    remove_diacritics: bool = False,
) -> str:
    """Normalize a single string for WER/CER computation.

    Parameters
    ----------
    text:
        Input string.
    lowercase:
        Lowercase the text.
    strip_punctuation:
        Remove punctuation characters.
    unicode_normalization:
        One of "NFC", "NFD", "NFKC", "NFKD", or "none".
    collapse_whitespace:
        Collapse runs of whitespace to a single space and strip ends.
    remove_diacritics:
        Strip combining marks (use with care for tonal languages).
    """
    if unicode_normalization and unicode_normalization.upper() != "NONE":
        form = unicode_normalization.upper()
        if form not in ("NFC", "NFD", "NFKC", "NFKD"):
            raise ValueError(f"Invalid unicode normalization form: {unicode_normalization}")
        text = unicodedata.normalize(cast(Literal["NFC", "NFD", "NFKC", "NFKD"], form), text)
    if remove_diacritics:
        text = "".join(
            c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
        )
    if lowercase:
        text = text.lower()
    if strip_punctuation:
        text = _PUNCT_RE.sub(" ", text)
    if collapse_whitespace:
        text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def normalize_corpus(
    texts: Iterable[str],
    *,
    lowercase: bool = True,
    strip_punctuation: bool = True,
    unicode_normalization: str = "NFC",
    collapse_whitespace: bool = True,
    remove_diacritics: bool = False,
) -> list[str]:
    """Normalize a list of strings with identical settings."""
    return [
        normalize_text(
            t,
            lowercase=lowercase,
            strip_punctuation=strip_punctuation,
            unicode_normalization=unicode_normalization,
            collapse_whitespace=collapse_whitespace,
            remove_diacritics=remove_diacritics,
        )
        for t in texts
    ]
