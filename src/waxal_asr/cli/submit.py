"""`waxal-submit` CLI entry point: generate the next submission CSV."""

from __future__ import annotations

from pathlib import Path

import typer

from waxal_asr.config import load_config
from waxal_asr.utils.logging import configure_logging, get_logger

app = typer.Typer(add_completion=False, help="Generate a competition submission.")


@app.command()
def main(
    config: Path = typer.Option(
        "configs/inference.yaml", "--config", "-c", help="Inference config."
    ),
) -> None:
    cfg = load_config(config)
    configure_logging(level=cfg.logging.level)
    log = get_logger("cli.submit")
    log.warning("Submission generator not yet implemented. See ROADMAP.md.")


if __name__ == "__main__":
    app()
