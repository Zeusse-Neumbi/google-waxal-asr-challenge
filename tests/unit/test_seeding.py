"""Tests for seeding reproducibility."""

import random

from waxal_asr.utils.seeding import seed_everything


def test_seeding_produces_repeatable_python_rng() -> None:
    seed_everything(123, deterministic=False)
    a = [random.random() for _ in range(5)]
    seed_everything(123, deterministic=False)
    b = [random.random() for _ in range(5)]
    assert a == b


def test_seeding_changes_with_different_seed() -> None:
    seed_everything(1, deterministic=False)
    a = [random.random() for _ in range(5)]
    seed_everything(2, deterministic=False)
    b = [random.random() for _ in range(5)]
    assert a != b
