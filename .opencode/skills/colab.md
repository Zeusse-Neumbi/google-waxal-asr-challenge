# Skill: colab

## Purpose
Run training and inference on Google Colab with Drive-backed storage.

## Inputs
- Google Drive mount, Colab runtime (T4/A100).

## Outputs
- Datasets, checkpoints, predictions stored on Drive; code on GitHub.

## Best Practices
- Clone the repo into `/content/`; mount Drive at `/content/drive`.
- Symlink `data/`, `checkpoints/`, `outputs/` to Drive-backed folders.
- Install `requirements-dev.txt` then `pip install -e .`.
- Use `hf_transfer` for fast model downloads.
- Save checkpoints directly to Drive to survive runtime disconnects.

## Common Mistakes
- Storing data/checkpoints in `/content/` (lost on disconnect).
- Forgetting to mount Drive at session start.
- Installing packages every cell instead of once.

## Examples
```python
from google.colab import drive
drive.mount("/content/drive")
```

## References
- Colab docs: https://colab.research.google.com/
