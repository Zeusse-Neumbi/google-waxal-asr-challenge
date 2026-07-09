# TRAINING

Methodology for fine-tuning ASR models on the WAXAL dataset.

---

## Principles

1. **Config-driven** — every hyperparameter lives in `configs/`, never in code.
2. **Reproducible** — fixed seeds, deterministic ops where feasible, recorded configs.
3. **Generalization-first** — early stopping on held-out validation WER/CER.
4. **Iterative** — baseline → analyze errors → targeted improvements → repeat.

---

## Training Loop

Implemented in `waxal_asr/training/trainer.py`.

- AMP (mixed precision) on GPU.
- Gradient accumulation for large effective batch sizes.
- Cosine or linear LR schedule with warmup.
- Checkpointing: best + last + epoch snapshots (configurable).
- Resume from checkpoint with optimizer + scheduler state.
- Optional gradient clipping and gradient checkpointing for memory.

---

## Standard Recipe

1. **Baseline**: pretrained Whisper-small, frozen encoder, fine-tune decoder.
2. **Full fine-tune**: unfreeze encoder, lower LR, longer warmup.
3. **Augmentation**: SpecAugment + noise + speed perturbation.
4. **Language-specific**: per-language sampling, language adapters.
5. **Decoding**: beam search + optional shallow LM fusion.

---

## Metrics Tracked Per Run

- Training loss
- Validation loss
- WER
- CER
- Combined score (`0.5 × WER + 0.5 × CER`)
- Epoch wall time
- GPU memory peak
- Learning rate trajectory

All metrics land in `experiments/<exp>/metrics.json` and (optionally) W&B.

---

## Augmentation

Configured via `configs/augmentation.yaml`:

- **SpecAugment** — time/frequency masking.
- **Noise** — additive noise from external corpora.
- **Speed perturbation** — factors {0.9, 1.0, 1.1}.

Augmentation is train-only and never applied to validation/test.

---

## Checkpoint Strategy

- Save: `last`, `best` (by combined score), and N most recent.
- Location: `outputs/models/<experiment_name>/`.
- Each checkpoint records: epoch, step, metrics, config hash, git SHA.

Never overwrite a checkpoint belonging to a previous experiment.
