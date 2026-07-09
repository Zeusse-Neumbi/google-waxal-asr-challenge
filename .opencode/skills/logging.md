# Skill: logging

## Purpose
Structured logging across the pipeline using `loguru`.

## Inputs
- Log messages + structured context.

## Outputs
- Console + file logs in `outputs/logs/` and `experiments/<exp>/logs/`.

## Best Practices
- Use `loguru` everywhere in `src/` — never `print()`.
- Add structured context: experiment id, step, epoch.
- Log every important event: training start/end, checkpoint save, eval, submission.
- Rotate + retain logs; never let them grow unbounded.

## Common Mistakes
- Using `print()` for diagnostics in committed code.
- Logging secrets or full transcripts at INFO level.
- Not flushing logs before a crash.

## Examples
```python
from waxal_asr.utils.logging import get_logger
log = get_logger(__name__)
log.info("training started", experiment="001", epoch=1)
```

## References
- loguru: https://github.com/Delgan/loguru
