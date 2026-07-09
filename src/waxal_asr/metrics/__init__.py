"""ASR metrics: WER, CER, combined score.

This module is *independent* of training code. It operates on lists of reference and
hypothesis strings after text normalization.
"""

from waxal_asr.metrics.text import normalize_corpus, normalize_text
from waxal_asr.metrics.wer import cer, combined_score, wer

__all__ = ["cer", "combined_score", "normalize_corpus", "normalize_text", "wer"]
