"""`waxal-train` CLI entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from waxal_asr.config import load_config
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

    from waxal_asr.utils.seeding import seed_everything

    seed_everything(cfg.repro.seed, deterministic=cfg.repro.deterministic)

    # TODO(experiment 001): wire to Trainer.
    log.warning("Trainer not yet implemented. See ROADMAP.md Phase 1.")
    sys.exit(0)


if __name__ == "__main__":
    app()
