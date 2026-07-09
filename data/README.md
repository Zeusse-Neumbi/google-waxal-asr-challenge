# data

Audio datasets and metadata. **Almost everything here is git-ignored** — datasets,
checkpoints, caches, and predictions live on Google Drive, not in Git.

## Layout

```
data/
├── raw/         # immutable original files (NEVER edit)
├── processed/   # cleaned, resampled, split data
├── interim/     # intermediate artifacts (feature caches, etc.)
├── external/    # auxiliary data (MUSAN noise, language models)
└── metadata/    # manifests, splits, language maps (committed)
```

## Rules

- **Raw data is immutable.** Never modify files in `data/raw/`.
- **No hardcoded paths.** Read paths from `configs/baseline.yaml` (`paths.*`).
- **Manifests are the source of truth.** `data/metadata/manifest.csv` maps
  `audio_path → transcript → language → split → duration`. Loaders consume manifests.
- Large audio files are git-ignored; only `.gitkeep` markers + `metadata/` are committed.
