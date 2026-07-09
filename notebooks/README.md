# notebooks

Jupyter notebooks. Each notebook has **one responsibility**. No business logic here —
reusable logic belongs in `src/waxal_asr/`.

## Order

| #   | Notebook                      | Purpose                          |
| --- | ----------------------------- | -------------------------------- |
| 01  | `01_setup.ipynb`              | Environment setup (Colab + Drive) |
| 02  | `02_dataset_analysis.ipynb`   | Dataset EDA + manifest generation |
| 03  | `03_training.ipynb`           | Training runs + visualization    |
| 04  | `04_evaluation.ipynb`         | Evaluation + metric dashboards   |
| 05  | `05_error_analysis.ipynb`     | Error analysis + stratification   |
| 06  | `06_submission.ipynb`         | Submission generation            |

## Rules

- If notebook code becomes reusable, move it into `src/waxal_asr/`.
- Run `nbstripout` before committing (installed via pre-commit) to keep diffs clean.
- Never load datasets/checkpoints with hardcoded paths — read from `configs/`.
