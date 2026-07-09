"""Typed configuration schemas (dataclasses).

All experiment/pipeline configuration is described by the dataclasses here. YAML files
in `configs/` are loaded via `loader.load_config`, interpolated, and validated against
these schemas. Never hardcode hyperparameters in code — read from a `Config`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass
class ProjectConfig:
    name: str = "waxal-asr"
    version: str = "0.1.0"
    seed: int = 42


@dataclass
class PathsConfig:
    data_raw: Path = Path("data/raw")
    data_processed: Path = Path("data/processed")
    data_interim: Path = Path("data/interim")
    data_external: Path = Path("data/external")
    metadata: Path = Path("data/metadata")
    manifests: Path = Path("data/metadata/manifest.csv")
    outputs: Path = Path("outputs")
    checkpoints: Path = Path("checkpoints")
    experiments: Path = Path("experiments")
    submissions: Path = Path("submissions")
    logs: Path = Path("outputs/logs")
    cache: Path = Path("data/interim/cache")


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    mono: bool = True
    normalize: Literal["peak", "rms", "none"] = "peak"
    min_duration_s: float = 0.5
    max_duration_s: float = 30.0


@dataclass
class ReproConfig:
    seed: int = 42
    deterministic: bool = True
    benchmark: bool = False
    cudnn_deterministic: bool = True


@dataclass
class OptimizerConfig:
    name: str = "adamw"
    lr: float = 1.0e-5
    weight_decay: float = 0.01
    betas: tuple[float, float] = (0.9, 0.999)
    eps: float = 1.0e-8


@dataclass
class SchedulerConfig:
    name: Literal["cosine", "linear", "constant"] = "cosine"
    warmup_ratio: float = 0.1
    num_cycles: int = 1


@dataclass
class CheckpointConfig:
    save_dir: Path = Path("outputs/models")
    save_best: bool = True
    save_last: bool = True
    save_top_k: int = 3
    monitor: Literal["wer", "cer", "combined", "val_loss"] = "combined"
    mode: Literal["min", "max"] = "min"


@dataclass
class EvaluationConfig:
    batch_size: int = 32
    normalize_text: bool = True
    lowercase: bool = True
    strip_punctuation: bool = True
    unicode_normalization: Literal["NFC", "NFD", "NFKC", "NFKD", "none"] = "NFC"
    metric: Literal["wer", "cer", "combined"] = "combined"


@dataclass
class TrackingConfig:
    backend: Literal["local", "wandb", "none"] = "local"
    wandb_project: str = "waxal-asr"
    wandb_entity: str | None = None
    log_every_n_steps: int = 50


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: Path = Path("outputs/logs/run.log")
    rotation: str = "10 MB"
    retention: str = "14 days"


@dataclass
class HardwareConfig:
    device: Literal["auto", "cpu", "cuda"] = "auto"
    fallback_to_cpu: bool = True


@dataclass
class Config:
    """Top-level configuration object.

    Attributes are populated from the merged YAML config. Any field missing from the YAML
    falls back to the dataclass default, ensuring forward compatibility.
    """

    project: ProjectConfig = field(default_factory=ProjectConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    repro: ReproConfig = field(default_factory=ReproConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    checkpoint: CheckpointConfig = field(default_factory=CheckpointConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    # Free-form sections that vary per experiment (training, model, augmentation, ...).
    raw: dict[str, Any] = field(default_factory=dict)
