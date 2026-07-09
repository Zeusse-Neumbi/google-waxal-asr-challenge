"""Audio preprocessing: validation, resampling, normalization."""

from __future__ import annotations

import torch

__all__ = ["normalize_audio", "trim_silence", "validate_audio"]


def normalize_audio(audio: torch.Tensor, mode: str = "peak") -> torch.Tensor:
    """Normalize a `[C, T]` (or `[T]`) audio tensor.

    Parameters
    ----------
    mode:
        "peak"  - divide by max absolute value.
        "rms"   - divide by root-mean-square.
        "none"  - return unchanged.
    """
    if mode == "none":
        return audio
    if audio.ndim == 1:
        audio = audio.unsqueeze(0)
        squeeze = True
    else:
        squeeze = False
    if mode == "peak":
        peak = audio.abs().max()
        audio = audio / (peak + 1e-8) if peak > 0 else audio
    elif mode == "rms":
        rms = torch.sqrt((audio**2).mean(dim=-1, keepdim=True) + 1e-8)
        audio = audio / rms
    else:
        raise ValueError(f"Unknown normalization mode: {mode}")
    return audio.squeeze(0) if squeeze else audio


def validate_audio(
    audio: torch.Tensor,
    sample_rate: int,
    min_duration_s: float = 0.5,
    max_duration_s: float = 30.0,
    min_sr: int = 8000,
) -> list[str]:
    """Return a list of issues found with the audio (empty list = OK)."""
    issues: list[str] = []
    if sample_rate < min_sr:
        issues.append(f"sample_rate {sample_rate} < {min_sr}")
    duration = audio.shape[-1] / sample_rate
    if duration < min_duration_s:
        issues.append(f"duration {duration:.2f}s < {min_duration_s}s")
    if duration > max_duration_s:
        issues.append(f"duration {duration:.2f}s > {max_duration_s}s")
    if not torch.isfinite(audio).all():
        issues.append("non-finite values (inf/nan)")
    return issues


def trim_silence(audio: torch.Tensor, threshold: float = 0.01) -> torch.Tensor:
    """Trim leading/trailing samples below `threshold` in absolute value."""
    if audio.ndim == 1:
        audio = audio.unsqueeze(0)
        squeeze = True
    else:
        squeeze = False
    mask = audio.abs() > threshold
    if not mask.any():
        return audio.squeeze(0) if squeeze else audio
    first = mask.any(dim=0).int().argmax().item()
    last = audio.shape[-1] - mask.any(dim=0).int().flip(0).argmax().item()
    out = audio[..., first:last]
    return out.squeeze(0) if squeeze else out
