"""Trainer orchestration.

TODO (experiment 001): implement the training loop honoring `configs/baseline.yaml`:
- AMP, gradient accumulation, gradient clipping.
- Cosine/linear schedulers with warmup.
- Save last/best/top-k checkpoints.
- Resume from checkpoint.
- Log metrics to `experiments/<exp>/metrics.json` + optional W&B.

Implemented in the Whisper-baseline experiment phase.
"""

from __future__ import annotations

__all__ = ["Trainer"]


class Trainer:
    """Placeholder trainer. Concrete implementation lands with experiment 001."""

    def __init__(self, config: object) -> None:
        self.config = config

    def fit(self) -> None:  # pragma: no cover
        raise NotImplementedError("Trainer will be implemented in experiment 001.")
