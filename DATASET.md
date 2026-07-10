# DATASET

Description of the data sources for the Google WAXAL ASR Challenge.

---

## Overview

The challenge uses two data sources:

1. **HuggingFace Dataset `google/WaxalNLP`** — the full WAXAL corpus of 27 African languages
   with audio + transcriptions. Used for model training and development.
2. **Zindi competition CSVs** — train/test IDs and metadata mapping to the HuggingFace data.

> **Data is NOT stored locally under `data/raw/`.** The primary data source is HuggingFace.
> Zindi CSVs (`Train.csv`, `Test.csv`, `SampleSubmission.csv`) live in the
> `google-waxal-asr-challenge20260630-10570-elxebu/` directory.

---

## Zindi CSV Format

### Train.csv
| Column | Description |
| --- | --- |
| `id` | Unique utterance ID (format: `<lang>_<number>`, e.g. `lug_96123`) |
| `transcription` | Ground-truth text |
| `language` | Language code (`lin`, `sna`, `lug`) |
| `original_split` | HuggingFace split origin (`train`, `validation`, `test`) |

### Test.csv
| Column | Description |
| --- | --- |
| `ID` | Utterance ID (same format as Train.csv) |

### SampleSubmission.csv
| Column | Description |
| --- | --- |
| `ID` | Utterance ID (must match Test.csv exactly) |
| `Target` | Predicted transcription text |

---

## Languages

The challenge focuses on 3 of the 27 WAXAL languages:

| Language | Code | Train.csv utterances |
| --- | --- | --- |
| Lingala | `lin` | 16,240 |
| Shona | `sna` | 15,817 |
| Luganda | `lug` | 6,119 |
| **Total** | | **38,176** |

---

## Splits

| Split | Purpose |
| --- | --- |
| train | Training only (from HuggingFace or `original_split=train`) |
| validation | Model selection (from HuggingFace or `original_split=validation`) |
| test | Phase 1 leaderboard (from Zindi Test.csv) |
| hidden | Phase 2 unseen recordings (released during last week) |

---

## Audio Properties (from WAXAL dataset)

- Sample rate: 16 kHz
- Channels: mono
- Format: various (HuggingFace handles conversion)

---

## Manifests

A manifest is a CSV mapping `id → transcription → language → split`.

The chat is not `audio_path` based — audio is loaded from HuggingFace by ID.
Manifests live in `data/metadata/` and are the single source of truth for dataset access.

---

## Phase 2

In the final week, a completely new test set is released (audio only). No metadata
(language, speaker, gender) will be provided. Models must rely on the speech signal alone.
