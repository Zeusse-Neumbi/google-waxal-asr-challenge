# Memory: dataset

Persistent notes about the WAXAL dataset. **Append-only.**

---

## Source
- HuggingFace: `google/WaxalNLP` (https://huggingface.co/datasets/google/WaxalNLP)
- Zindi competition CSVs: `google-waxal-asr-challenge20260630-10570-elxebu/`

## Zindi CSV files (competition data)
| File | Columns | Description |
| --- | --- | --- |
| Train.csv | `id`, `transcription`, `language`, `original_split` | Training data with transcriptions |
| Test.csv | `ID` | Test IDs only (no transcriptions) |
| SampleSubmission.csv | `ID`, `Target` | Example submission format |

## Languages (from Train.csv)
| Language | Code | Utterances |
| --- | --- | --- |
| Lingala | lin | 16,240 |
| Shona | sna | 15,817 |
| Luganda | lug | 6,119 |
| **Total** | | **38,176** |

NOTE: Some Train.csv rows have malformed quoting (commas inside unquoted transcriptions spill into the `language` column). These are ~25 rows out of 38k — small enough to handle case-by-case.

## HuggingFace dataset (`google/WaxalNLP`)
- 27 African languages, ~500+ hours of speech
- Audio paired with transcriptions
- Includes splits: `train`, `validation`, `test`
- At 16 kHz mono audio
- Used for Phase 1 model development

## Test.csv format (Zindi)
- Single column `ID` only — no audio paths, no metadata
- ID format: `<lang>_<number>` (e.g. `lug_96114`)
- Must transcribe audio from HuggingFace corresponding to these IDs

## Manifest schema (for CSV processing)
- Required columns: `id`, `transcription`, `language`
- No `audio_path` column — data loaded from HuggingFace
- Use `original_split` for train/validation splitting

## Audio properties (from WAXAL paper)
- Sample rate: 16 kHz
- Channels: mono
- Format: various (converted as needed)

## Quality issues found
- (TODO after EDA)
