"""`waxal-submit` CLI entry point: generate the next submission CSV.

Produces a CSV with columns `ID,Target` matching the Zindi competition spec.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from waxal_asr.config import load_config
from waxal_asr.utils.logging import configure_logging, get_logger

app = typer.Typer(add_completion=False, help="Generate a competition submission.")


@app.command()
def main(
    config: Path = typer.Option(
        "configs/inference.yaml", "--config", "-c", help="Inference config."
    ),
    predictions_csv: Path = typer.Option(
        "outputs/predictions.csv",
        "--predictions",
        "-p",
        help="CSV with predictions (from waxal-infer).",
    ),
    test_csv: Path | None = typer.Option(None, "--test-csv", "-t", help="Override Test.csv path."),
    output_dir: Path | None = typer.Option(
        None, "--output-dir", "-o", help="Submission output directory."
    ),
) -> None:
    cfg = load_config(config)
    configure_logging(level=cfg.logging.level)
    log = get_logger("cli.submit")

    out_dir = output_dir or Path(cfg.submission.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load test CSV for ID mapping
    if test_csv is None:
        test_csv = Path(cfg.submission.test_csv) if cfg.submission.test_csv else None
    if test_csv is None:
        raise typer.BadParameter(
            "Test CSV path not provided (set submission.test_csv in config or use --test-csv)."
        )
    if not test_csv.exists():
        raise typer.BadParameter(f"Test CSV not found: {test_csv}")
    test_df = pd.read_csv(test_csv)
    ids = list(test_df["ID"].values)

    # Load predictions
    if not predictions_csv.exists():
        log.warning(
            "Predictions CSV not found: {}. Generating placeholder submission.",
            predictions_csv,
        )
        preds = [""] * len(ids)
    else:
        pred_df = pd.read_csv(predictions_csv)
        preds = list(pred_df["Target"].values)
        if len(preds) != len(ids):
            log.warning(
                "Prediction count ({}) doesn't match test IDs ({}). Padding.",
                len(preds),
                len(ids),
            )
            preds = preds[: len(ids)] + [""] * (len(ids) - len(preds))

    df = pd.DataFrame({"ID": ids, "Target": preds})

    # Auto-increment submission number
    existing = sorted(out_dir.glob("submission_*.csv"))
    next_num = 1
    if existing:
        last = int(existing[-1].stem.split("_")[1])
        next_num = last + 1

    out_path = out_dir / f"submission_{next_num:03d}.csv"
    df.to_csv(out_path, index=False)
    log.info("submission written", path=str(out_path), rows=len(df))

    # Validate
    written = pd.read_csv(out_path)
    assert list(written.columns) == ["ID", "Target"], f"Unexpected columns: {written.columns}"
    assert len(written) == len(ids), f"Row count mismatch: {len(written)} vs {len(ids)}"
    log.info("submission validated", columns=list(written.columns), rows=len(written))


if __name__ == "__main__":
    app()
