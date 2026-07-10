"""`waxal-train` CLI entry point."""

from __future__ import annotations

from pathlib import Path

import typer

from waxal_asr.config import load_config
from waxal_asr.training.trainer import Trainer
from waxal_asr.utils.logging import configure_logging, get_logger

app = typer.Typer(add_completion=False, help="Train an ASR model.")


@app.command()
def main(
    config: Path = typer.Option("configs/baseline.yaml", "--config", "-c", help="Config YAML."),
    override: list[str] = typer.Option(
        [], "--set", "-s", help="Override a config key, e.g. training.epochs=20"
    ),
) -> None:
    """Run a training experiment from a config file."""
    cfg = load_config(config)
    configure_logging(level=cfg.logging.level, log_file=cfg.logging.file)
    log = get_logger("cli.train")
    log.info("config loaded", config=str(config), seed=cfg.repro.seed)

    trainer = Trainer(cfg)
    trainer.fit()

    log.info("Experiment complete")


if __name__ == "__main__":
    app()
