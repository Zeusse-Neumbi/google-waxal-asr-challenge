"""Tests for evaluation report generation."""

import json
from pathlib import Path

from waxal_asr.evaluation import evaluate


def test_evaluate_writes_metrics_and_predictions(tmp_path: Path) -> None:
    refs = ["Hello, world!", "the quick brown fox"]
    hyps = ["hello world", "the quick red fox"]
    metrics = evaluate(refs, hyps, output_dir=tmp_path)

    assert "wer" in metrics and "cer" in metrics and "combined" in metrics
    assert metrics["n_utterances"] == 2
    assert 0.0 < metrics["wer"] < 1.0

    metrics_file = tmp_path / "metrics.json"
    preds_file = tmp_path / "predictions.csv"
    assert metrics_file.exists()
    assert preds_file.exists()

    loaded = json.loads(metrics_file.read_text())
    assert loaded["n_utterances"] == 2

    csv_text = preds_file.read_text()
    assert "reference" in csv_text and "hypothesis" in csv_text


def test_evaluate_mismatched_lengths_raises(tmp_path: Path) -> None:
    import pytest

    with pytest.raises(ValueError):
        evaluate(["a", "b"], ["a"], output_dir=tmp_path)
