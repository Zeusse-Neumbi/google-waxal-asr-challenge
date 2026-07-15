"""Evaluation report generation.

Takes references + hypotheses, normalizes, computes metrics, stratifies, and writes
a report into the experiment directory. Independent of training code.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import cast

import pandas as pd

from waxal_asr.metrics import cer, combined_score, normalize_corpus, wer

__all__ = ["evaluate"]


def evaluate(
    references: Iterable[str],
    hypotheses: Iterable[str],
    output_dir: str | Path,
    *,
    ids: Iterable[str] | None = None,
    languages: Iterable[str] | None = None,
    durations: Iterable[float] | None = None,
    lowercase: bool = True,
    strip_punctuation: bool = True,
    unicode_normalization: str = "NFC",
) -> dict[str, float]:
    """Normalize, compute metrics, and write a report + predictions CSV.

    Returns the metrics dict.
    """
    references = list(references)
    hypotheses = list(hypotheses)
    if len(references) != len(hypotheses):
        raise ValueError("references and hypotheses must be the same length")

    norm_ref = normalize_corpus(
        references,
        lowercase=lowercase,
        strip_punctuation=strip_punctuation,
        unicode_normalization=unicode_normalization,
    )
    norm_hyp = normalize_corpus(
        hypotheses,
        lowercase=lowercase,
        strip_punctuation=strip_punctuation,
        unicode_normalization=unicode_normalization,
    )

    metrics = {
        "wer": wer(norm_ref, norm_hyp),
        "cer": cer(norm_ref, norm_hyp),
        "combined": combined_score(norm_ref, norm_hyp),
        "n_utterances": len(norm_ref),
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))

    preds = pd.DataFrame(
        {
            "id": list(ids) if ids is not None else range(len(norm_ref)),
            "reference": norm_ref,
            "hypothesis": norm_hyp,
            "language": (
                list(languages)
                if languages is not None
                else cast("list[str]", [None] * len(norm_ref))
            ),
            "duration": (
                list(durations)
                if durations is not None
                else cast("list[float]", [None] * len(norm_ref))
            ),
        }
    )
    preds.to_csv(output_dir / "predictions.csv", index=False)
    return metrics
