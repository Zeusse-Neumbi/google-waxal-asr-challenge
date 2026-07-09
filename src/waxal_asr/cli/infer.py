"""`waxal-infer` CLI entry point."""

from __future__ import annotations

from pathlib import Path

import typer

from waxal_asr.config import load_config
from waxal_asr.utils.logging import configure_logging, get_logger

app = typer.Typer(add_completion=False, help="Run inference on a set of audio files.")


@app.command()
def main(
    config: Path = typer.Option(
        "configs/inference.yaml", "--config", "-c", help="Inference config."
    ),
    audio_dir: Path | None = typer.Option(
        None, "--audio-dir", "-a", help="Override test audio dir."
    ),
) -> None:
    cfg = load_config(config)
    configure_logging(level=cfg.logging.level)
    log = get_logger("cli.infer")
    log.warning("Inference engine not yet implemented. See ROADMAP.md.")


if __name__ == "__main__":
    app()
