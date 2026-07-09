# Skill: python

## Purpose
Project Python conventions: style, typing, packaging, tooling.

## Inputs
- Python source in `src/`, `tests/`, `scripts/`.

## Outputs
- Linted, formatted, type-checked, tested code.

## Best Practices
- Python ≥ 3.11.
- Type hints + docstrings on all public APIs.
- `pathlib.Path` for paths.
- `dataclasses` / `attrs` for structured config.
- `loguru` for logging.
- Run: `ruff check . && black --check . && mypy -p waxal_asr && pytest`.

## Common Mistakes
- `print()` in `src/`.
- String-concatenated paths.
- Magic numbers in code (move to config).
- Untyped public functions.

## Examples
```bash
ruff check . && black . && mypy -p waxal_asr && pytest
```

## References
- `pyproject.toml` for tool config.
- `PROJECT_RULES.md` §5.
