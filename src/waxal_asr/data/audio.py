"""Audio loading utilities.

`load_audio` is the single entry point for reading audio files. Returns a mono tensor
resampled to `target_sr`. Backend: torchaudio (fast), librosa (fallback).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

__all__ = ["load_audio"]


def load_audio(
    path: str | Path,
    target_sr: int = 16000,
    mono: bool = True,
    backend: str = "auto",
) -> tuple[Any, int]:
    """Load an audio file as a torch tensor `[C, T]` (mono: `[1, T]`).

    Parameters
    ----------
    path:
        Path to the audio file (wav, flac, mp3, ogg).
    target_sr:
        Target sample rate. The audio is resampled to this rate.
    mono:
        If True, downmix to mono.
    backend:
        "torchaudio" | "librosa" | "auto".

    Returns
    -------
    (audio, sample_rate)
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    if backend in ("auto", "torchaudio"):
        try:
            import torch
            import torchaudio

            waveform, sr = torchaudio.load(str(path))  # [C, T]
            if mono and waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            if sr != target_sr:
                waveform = torchaudio.functional.resample(waveform, sr, target_sr)
                sr = target_sr
            return waveform, sr
        except Exception:
            if backend == "torchaudio":
                raise

    # librosa fallback
    import librosa
    import torch

    audio_np, sr = librosa.load(str(path), sr=target_sr, mono=mono)
    if audio_np.ndim == 1:
        audio_np = audio_np[np.newaxis, :]
    return torch.from_numpy(audio_np).float(), sr
