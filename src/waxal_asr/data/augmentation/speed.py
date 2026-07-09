"""Speed perturbation augmentation."""

from __future__ import annotations

import torch
import torchaudio

__all__ = ["speed_perturb"]


def speed_perturb(audio: torch.Tensor, sample_rate: int, factor: float = 1.0) -> torch.Tensor:
    """Time-stretch audio by `factor` using SoX speed effect (preserves pitch poorly).

    For higher-quality pitch-preserving stretch, use a phase vocoder.
    """
    if factor == 1.0:
        return audio
    if audio.ndim == 1:
        audio = audio.unsqueeze(0)
        squeeze = True
    else:
        squeeze = False
    effects = [["speed", str(factor)], ["rate", str(sample_rate)]]
    out, _ = torchaudio.sox_effects.apply_effects_tensor(audio, sample_rate, effects)
    return out.squeeze(0) if squeeze else out
