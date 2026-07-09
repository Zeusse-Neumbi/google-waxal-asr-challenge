# DATASET

Description of the Google WAXAL dataset used in this challenge.

---

## Overview

The Google WAXAL dataset is a multilingual speech corpus provided for the WAXAL ASR
Challenge. It contains audio recordings paired with text transcriptions across multiple
languages (primarily West African languages).

> **TODO**: fill in authoritative statistics once the dataset is loaded into `data/raw/`.
> The numbers below are placeholders pending the first EDA pass (see
> `notebooks/02_dataset_analysis.ipynb`).

---

## Directory Layout

```
data/
├── raw/         # immutable, original files from the challenge
├── processed/   # cleaned, resampled, split data
├── interim/     # intermediate artifacts (e.g. feature caches)
├── external/    # auxiliary data (noise corpora, LMs)
└── metadata/    # manifests, splits, language maps
```

**Raw data is immutable.** Never edit files under `data/raw/`.

---

## Splits

| Split   | Purpose                          |
| ------- | -------------------------------- |
| train   | Training only                    |
| dev     | Validation, model selection      |
| test    | Held-out, local evaluation only  |
| hidden  | Leaderboard (not available)      |

---

## Audio Properties

To be determined via EDA. Track:

- Sample rate distribution
- Duration distribution
- Channels (mono/stereo)
- Bit depth
- Clipping / silence ratio
- SNR estimates

---

## Languages

Track per-language:

- Number of utterances
- Total audio hours
- Character set / script
- Code-switching frequency

---

## Manifests

A manifest is a CSV mapping `audio_path → transcript → language → duration → split`.

Manifests live in `data/metadata/` and are the single source of truth for dataset access.
Dataset loaders (`waxal_asr/data/`) never hardcode paths — they read manifests.
