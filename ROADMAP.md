# ROADMAP

What's next for the WAXAL ASR framework.

Legend: ✅ done · 🚧 in progress · 📋 planned · 💡 idea

---

## Phase 0 — Bootstrap ✅

- ✅ Repository structure
- ✅ Config system scaffolding
- ✅ CI scaffolding
- ✅ Documentation skeleton
- ✅ `.opencode/` AI workspace

## Phase 1 — Data & Baseline 📋

- 📋 Dataset download & manifest generation
- 📋 `notebooks/02_dataset_analysis.ipynb` EDA
- 📋 `waxal_asr/data/` audio loader + preprocessing
- 📋 Whisper-small zero-shot baseline (`exp001`)
- 📋 WER/CER metrics implementation + tests

## Phase 2 — Fine-tuning 📋

- 📋 Trainer implementation (`waxal_asr/training/trainer.py`)
- 📋 `configs/whisper-small.yaml` fine-tune run
- 📋 Augmentation: SpecAugment, noise, speed perturbation
- 📋 Experiment logging + W&B integration
- 📋 First submission (`submissions/submission_001.csv`)

## Phase 3 — Stronger Models 📋

- 📋 Whisper-medium / large-v3 fine-tuning
- 📋 Whisper Turbo for fast inference
- 📋 Beam-search decoding (`waxal_asr/decoding/`)
- 📋 Shallow LM fusion (optional)

## Phase 4 — Model Diversity 📋

- 📋 MMS adapter
- 📋 wav2vec2 / XLSR CTC fine-tuning
- 📋 SeamlessM4T evaluation
- 📋 Canary evaluation
- 📋 Model ensemble / selection per language

## Phase 5 — Error Analysis & Hardening 📋

- 📋 `notebooks/05_error_analysis.ipynb`
- 📋 Per-language error breakdown
- 📋 Duration / SNR / speaker stratified evaluation
- 📋 Robustness: noise, accent, code-switching
- 📋 Final submission strategy

## Phase 6 — Framework Polish 💡

- 💡 Documentation site (mkdocs)
- 💡 Reproducibility CI (deterministic seed check)
- 💡 Public release of the framework beyond the competition

---

## Decision Log

Each phase is informed by the previous phase's error analysis. Never skip analysis.
