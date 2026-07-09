"""waxal_asr — multilingual ASR framework for the Google WAXAL ASR Challenge.

This package contains the production source for the WAXAL ASR pipeline. All reusable
logic lives here; notebooks are reserved for EDA, visualization, and quick experiments.

Subpackages
-----------
config        - load, validate, and merge YAML configs into typed dataclasses.
data          - dataset loaders, audio IO, preprocessing, augmentation.
models        - unified model interface + concrete architectures.
training      - trainer, loops, schedulers, checkpointing.
inference     - batched inference + post-processing.
evaluation    - metrics orchestration, error analysis, reports (independent of training).
metrics       - WER, CER, combined score.
decoding      - greedy, beam-search, LM-fused decoders.
pipeline     - end-to-end orchestration of train/eval/infer.
visualization - plots, error heatmaps, dashboards.
utils         - logging, seeding, IO, audio utilities.
cli           - Typer entry points (waxal-train, waxal-eval, waxal-infer, waxal-submit).
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
