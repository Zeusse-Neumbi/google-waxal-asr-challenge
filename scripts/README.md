# scripts

Operational scripts (CLI entry points, dataset preparation, manifest generation).

These scripts call into `src/waxal_asr/` — they should contain no business logic
themselves, only orchestration.

## Conventions

- One script per task.
- Accept config paths / CLI args; never hardcode values.
- Use `loguru` (via `waxal_asr.utils.logging`) — no `print()`.
- Type-hint everything.

## Planned scripts

- `build_manifest.py` — scan `data/raw/`, produce `data/metadata/manifest.csv`.
- `download_dataset.py` — fetch the WAXAL dataset.
- `prepare_noise.py` — prepare the MUSAN noise corpus in `data/external/`.
- `verify_setup.py` — sanity-check the environment (Python, GPU, deps, paths).
