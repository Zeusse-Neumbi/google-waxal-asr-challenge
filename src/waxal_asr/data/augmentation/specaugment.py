"""SpecAugment: time/frequency masking on mel-spectrograms."""

from __future__ import annotations

import torch

__all__ = ["spec_augment"]


def spec_augment(
    features: torch.Tensor,
    time_mask_param: int = 30,
    freq_mask_param: int = 15,
    n_time_masks: int = 2,
    n_freq_masks: int = 2,
    mask_value: float = 0.0,
) -> torch.Tensor:
    """Apply SpecAugment to a `[batch, n_mels, time]` or `[n_mels, time]` tensor.

    Parameters mirror the original SpecAugment paper (Park et al., 2019).
    """
    squeeze = False
    if features.ndim == 2:
        features = features.unsqueeze(0)
        squeeze = True
    elif features.ndim != 3:
        raise ValueError(f"Expected 2D or 3D tensor, got shape {features.shape}")

    out = features.clone()
    batch, n_mels, n_time = out.shape
    for b in range(batch):
        for _ in range(n_freq_masks):
            if freq_mask_param > 0 and n_mels > 0:
                f = int(torch.randint(0, min(freq_mask_param, n_mels), (1,)).item())
                f0 = int(torch.randint(0, n_mels - f + 1, (1,)).item())
                out[b, f0 : f0 + f, :] = mask_value
        for _ in range(n_time_masks):
            if time_mask_param > 0 and n_time > 0:
                t = int(torch.randint(0, min(time_mask_param, n_time), (1,)).item())
                t0 = int(torch.randint(0, n_time - t + 1, (1,)).item())
                out[b, :, t0 : t0 + t] = mask_value
    return out.squeeze(0) if squeeze else out
