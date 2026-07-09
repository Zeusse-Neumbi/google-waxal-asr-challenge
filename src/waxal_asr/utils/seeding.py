"""Reproducibility: seed every RNG used by the pipeline.

Call `seed_everything(seed)` at the start of every script/experiment before any model
or dataloader construction.
"""

from __future__ import annotations

import contextlib
import os
import random

__all__ = ["seed_everything"]


def seed_everything(seed: int, deterministic: bool = True) -> None:
    """Seed Python, NumPy, and PyTorch RNGs.

    Parameters
    ----------
    seed:
        Integer seed.
    deterministic:
        If True, configure PyTorch for deterministic cuDNN behavior (slower, but
        reproducible).
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:  # pragma: no cover
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        # Enable deterministic algorithms where possible.
        if hasattr(torch, "use_deterministic_algorithms"):
            with contextlib.suppress(RuntimeError, TypeError):
                torch.use_deterministic_algorithms(deterministic, warn_only=True)
    except ImportError:  # pragma: no cover
        pass
