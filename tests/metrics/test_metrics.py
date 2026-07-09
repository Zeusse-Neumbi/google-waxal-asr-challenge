"""Unit tests for the metrics module (independent of training)."""

import pytest

from waxal_asr.metrics import cer, combined_score, normalize_corpus, normalize_text, wer
from waxal_asr.metrics.wer import edit_distance


class TestEditDistance:
    @pytest.mark.parametrize(
        "ref,hyp,expected",
        [
            ([], [], 0),
            (["a"], [], 1),
            ([], ["a"], 1),
            (["a"], ["a"], 0),
            (["a", "b", "c"], ["a", "b", "c"], 0),
            (["a", "b", "c"], ["a", "x", "c"], 1),  # substitution
            (["a", "b"], ["a", "b", "c"], 1),  # insertion
            (["a", "b", "c"], ["a", "c"], 1),  # deletion
            (["k", "i", "t", "t", "e", "n"], ["s", "i", "t", "t", "i", "n", "g"], 3),
        ],
    )
    def test_edit_distance(self, ref, hyp, expected):
        assert edit_distance(ref, hyp) == expected


class TestWER:
    def test_perfect_match(self):
        refs = ["hello world", "the quick brown fox"]
        hyps = ["hello world", "the quick brown fox"]
        assert wer(refs, hyps) == 0.0

    def test_one_substitution(self):
        refs = ["hello world"]
        hyps = ["hello there"]
        assert wer(refs, hyps) == pytest.approx(0.5)

    def test_empty_reference_returns_zero(self):
        # No reference words → denominator zero → defined as 0.0.
        assert wer([""], ["something"]) == 0.0

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            wer(["a", "b"], ["a"])


class TestCER:
    def test_perfect_matches(self):
        refs = ["abc", "def"]
        hyps = ["abc", "def"]
        assert cer(refs, hyps) == 0.0

    def test_single_char_substitution(self):
        refs = ["abcd"]  # 4 chars
        hyps = ["abxd"]  # 1 substitution
        assert cer(refs, hyps) == pytest.approx(0.25)


class TestCombinedScore:
    def test_combined_is_average(self):
        refs = ["hello world"]
        hyps = ["hello there"]
        w = wer(refs, hyps)
        c = cer(refs, hyps)
        assert combined_score(refs, hyps) == pytest.approx(0.5 * w + 0.5 * c)


class TestNormalization:
    def test_lowercase(self):
        assert normalize_text("HeLLo", lowercase=True) == "hello"

    def test_strip_punctuation(self):
        assert normalize_text("hello, world!", strip_punctuation=True) == "hello world"

    def test_collapse_whitespace(self):
        assert normalize_text("hello    world", collapse_whitespace=True) == "hello world"

    def test_unicode_nfc(self):
        # é as composed vs decomposed should normalize consistently.
        composed = "caf\u00e9"
        decomposed = "cafe\u0301"
        assert normalize_text(composed, unicode_normalization="NFC") == normalize_text(
            decomposed, unicode_normalization="NFC"
        )

    def test_corpus_normalization(self):
        out = normalize_corpus(["A, B.", "C!"], lowercase=True, strip_punctuation=True)
        assert out == ["a b", "c"]
