"""`waxal-eval` CLI entry point."""

from __future__ import annotations

from pathlib import Path

import typer

from waxal_asr.config import load_config
from waxal_asr.evaluation import evaluate
from waxal_asr.utils.logging import configure_logging, get_logger

app = typer.Typer(add_completion=False, help="Evaluate predictions against references.")


@app.command()
def main(
    config: Path = typer.Option("configs/evaluation.yaml", "--config", "-c", help="Eval config."),
    references: Path | None = typer.Option(
        None, "--references", "-r", help="References CSV (col: reference)."
    ),
    hypotheses: Path | None = typer.Option(
        None, "--hypotheses", "-p", help="Predictions CSV (col: hypothesis)."
    ),
    output_dir: Path = typer.Option(
        Path("outputs"), "--output-dir", "-o", help="Where to write the report."
    ),
) -> None:
    cfg = load_config(config)
    configure_logging(level=cfg.logging.level)
    log = get_logger("cli.evaluate")

    import pandas as pd

    if references is None or hypotheses is None:
        raise typer.BadParameter("Both --references and --hypotheses are required for now.")

    ref_df = pd.read_csv(references)
    hyp_df = pd.read_csv(hypotheses)
    refs = ref_df["reference"].astype(str).tolist()
    hyps = hyp_df["hypothesis"].astype(str).tolist()
    ids = ref_df["id"].tolist() if "id" in ref_df.columns else None

    metrics = evaluate(
        refs,
        hyps,
        output_dir=output_dir,
        ids=ids,
        lowercase=cfg.evaluation.lowercase,
        strip_punctuation=cfg.evaluation.strip_punctuation,
        unicode_normalization=cfg.evaluation.unicode_normalization,
    )
    log.info(
        "evaluation complete",
        **{k: (v if not isinstance(v, float) else round(v, 4)) for k, v in metrics.items()},
    )


if __name__ == "__main__":
    app()
