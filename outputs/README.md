# outputs

Run outputs (git-ignored). Created automatically by the pipeline.

```
outputs/
├── models/        # checkpoints from training
├── logs/          # loguru file logs
├── figures/       # generated plots
├── predictions/   # per-experiment prediction CSVs (also copied into experiments/)
├── temporary/     # scratch space
└── coverage/      # pytest coverage reports (CI)
```

Nothing here is committed except `.gitkeep` markers. On Google Colab, symlink this
directory to a Drive-backed folder to survive runtime disconnects.
