"""Additive noise augmentation."""

from __future__ import annotations

import torch

__all__ = ["add_noise"]


def add_noise(
    audio: torch.Tensor,
    noise: torch.Tensor,
    snr_db: float = 15.0,
) -> torch.Tensor:
    """Mix `noise` into `audio` at a target SNR (dB).

    Parameters
    ----------
    audio:
        Clean speech tensor.
    noise:
        Noise tensor (same sample rate). Trimmed/padded to match audio length.
    snr_db:
        Target signal-to-noise ratio in decibels.
    """
    if audio.shape != noise.shape:
        n = audio.shape[-1]
        if noise.shape[-1] < n:
            pad = n - noise.shape[-1]
            noise = torch.nn.functional.pad(noise, (0, pad))
        noise = noise[..., :n]
    signal_power = (audio**2).mean()
    noise_power = (noise**2).mean() + 1e-8
    snr_linear = 10.0 ** (snr_db / 10.0)
    scale = torch.sqrt(signal_power / (noise_power * snr_linear) + 1e-8)
    return audio + scale * noise
