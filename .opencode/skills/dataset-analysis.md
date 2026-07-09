# Skill: dataset-analysis

## Purpose
Profile the WAXAL dataset: durations, sample rates, languages, transcripts, splits, and
data-quality issues.

## Inputs
- Manifest CSV (`audio_path, transcript, language, split, duration`).

## Outputs
- `notebooks/02_dataset_analysis.ipynb` outputs:
  - duration histogram
  - sample-rate distribution
  - per-language utterance + hour counts
  - transcript length distribution
  - silence / clipping / SNR summary
- Updated `DATASET.md` statistics table.

## Best Practices
- Compute stats per split (train/dev/test) separately.
- Cache duration stats in the manifest to avoid re-reading audio.
- Surface class imbalance across languages early.

## Common Mistakes
- Reporting global stats that hide per-language imbalance.
- Forgetting to deduplicate utterances.
- Counting hours without excluding silence.

## Examples
```python
from waxal_asr.data.analysis import summarize_manifest
summary = summarize_manifest("data/metadata/manifest.csv")
```

## References
- See `DATASET.md` for the schema contract.
