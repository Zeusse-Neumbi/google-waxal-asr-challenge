# Memory: competition

Persistent notes about the Google WAXAL ASR Challenge. **Append-only. Never delete.**

---

## Basics
- Name: Google WAXAL ASR Challenge
- Host: Zindi (https://zindi.africa/competitions/google-waxal-asr-challenge/)
- Dataset: Google WAXAL Dataset from HuggingFace `google/WaxalNLP`
- Metric: `0.5 × WER + 0.5 × CER` (lower is better) — balanced word-level and character-level accuracy
- Eval: two-phase — Phase 1 uses provided test split on leaderboard; Phase 2 uses unseen recordings
- Final ranking: Phase 2 performance determines winners

## Languages
- 27 total African languages in WAXAL dataset
- Focus languages: Lingala (`lin`), Shona (`sna`), Luganda (`lug`)
- Challenge data contains only these 3 languages

## Timeline
- Start: June 26, 2026
- Close: August 2, 2026
- Reveal: August 2, 2026 (private leaderboard)
- Winners announced at Deep Learning Indaba: August 2-7, 2026

## Phases
### Phase 1 (Jun 26 ~ Jul 25)
- Use WAXAL train/validation/test splits from HuggingFace
- Build ASR models, submit predicted transcriptions as `ID,Target` CSV
- Test set has ground-truth labels — submitting those will be treated as cheating
- Public LB uses ~20% of test data
- Participants may supplement with other publicly available open-source speech/language datasets

### Phase 2 (last ~week before close)
- New unseen test set released (audio only)
- No metadata provided — no language, speaker, gender, or other auxiliary info
- Model must rely on speech signal itself
- Private LB uses ~80% of Phase 2 test data
- Final ranking determined by Phase 2 performance

## Data files (Zindi)
| File | Columns | Rows |
| --- | --- | --- |
| Train.csv | `id`, `transcription`, `language`, `original_split` | ~39k |
| Test.csv | `ID` (only) | ~4,254 |
| SampleSubmission.csv | `ID`, `Target` | ~4,254 |

## Dataset stats (Train.csv)
| Language | ISO | Utterances |
| --- | --- | --- |
| Lingala | lin | 16,240 |
| Shona | sna | 15,817 |
| Luganda | lug | 6,119 |

## Prizes
- 1st: $4,000 USD
- 2nd: $2,500 USD
- 3rd: $2,000 USD
- Best African participant: $1,500 USD (can also win overall prize)
- Total: $10,000 USD

## Rules
- Open-source languages and tools only
- Open to all
- Max team size: 4
- Max submissions: 5 per day, 200 total
- Top 10 on private LB must submit code for review (48h deadline)
- CC-BY 4.0 data license
- Code sharing across non-team accounts not allowed

## Submission format
- CSV with columns: `ID`, `Target`
- `ID` must match Test.csv IDs exactly
- `Target` is the predicted transcription text
- Validate schema before uploading
- Must select 2 final submissions before close (default: 2 best public)

## Key dates
- 2026-06-26 — competition starts
- 2026-07-09 — repository bootstrapped
- 2026-08-02 — competition closes
- 2026-08-02 — winners revealed at Deep Learning Indaba

## External data
- Allowed: publicly available open-source speech/language datasets
- Must be legally licensed for research/development
- Must disclose in final solution documentation
