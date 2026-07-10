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
class DatasetConfig:
    dataset_id: str = "google/WaxalNLP"
    language: str = "sna"
    streaming: bool = True
    sample_rate: int = 16000
    max_train_samples: int | None = None
    num_validation_examples: int = 200


@dataclass
class ModelConfig:
    model_id: str = "google/gemma-3n-E2B-it"
    model_type: Literal["gemma3n", "whisper"] = "gemma3n"
    torch_dtype: Literal["bfloat16", "float16", "float32"] = "bfloat16"
    load_in_4bit: bool = False
    attn_implementation: Literal["eager", "sdpa", "flash_attention_2"] = "eager"
    device_map: str = "auto"


@dataclass
class LoraConfig:
    enabled: bool = True
    r: int = 8
    alpha: int = 16
    dropout: float = 0.0
    target_modules: tuple[str, ...] = ("v_proj", "o_proj")
    bias: Literal["none", "all", "lora_only"] = "none"
    use_rslora: bool = False
    use_dora: bool = False


@dataclass
class ChatConfig:
    system_message: str = "You are an assistant that transcribes speech accurately."
    user_message: str = "Please transcribe this audio."


@dataclass
class TrainingConfig:
    max_steps: int = 500
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 8
    gradient_checkpointing: bool = True
    max_seq_length: int = 64
    logging_steps: int = 10
    eval_steps: int = 100
    save_steps: int = 100
    save_total_limit: int = 3
    eval_strategy: str = "steps"
    packing: bool = False
    dataloader_num_workers: int = 2
    report_to: str = "none"
    run_name: str | None = None
    remove_unused_columns: bool = False


@dataclass
class SubmissionConfig:
    output_dir: Path = Path("submissions")
    test_csv: Path | None = None
    next_number: int | None = None
    schema: dict = field(default_factory=lambda: {"columns": ["ID", "Target"]})
    validate: bool = True


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
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    lora: LoraConfig = field(default_factory=LoraConfig)
    chat: ChatConfig = field(default_factory=ChatConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    submission: SubmissionConfig = field(default_factory=SubmissionConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    augmentation: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
