"""`waxal-infer` CLI entry point."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import typer
from tqdm import tqdm

from waxal_asr.config import load_config
from waxal_asr.data.dataset import load_waxal_dataset
from waxal_asr.models.registry import build_model
from waxal_asr.utils.logging import configure_logging, get_logger

app = typer.Typer(add_completion=False, help="Run inference with a trained model.")


@app.command()
def main(
    config: Path = typer.Option("configs/baseline.yaml", "--config", "-c", help="Config YAML."),
    checkpoint: str = typer.Option(None, "--checkpoint", help="Adapter/model checkpoint path."),
    output: Path = typer.Option(
        "outputs/predictions.csv", "--output", "-o", help="Output CSV path."
    ),
    num_samples: int = typer.Option(200, "--num-samples", help="Number of test samples."),
    batch_size: int = typer.Option(4, "--batch-size", help="Inference batch size."),
) -> None:
    """Run batched inference on the test split and save predictions."""
    cfg = load_config(config)
    configure_logging(level=cfg.logging.level, log_file=cfg.logging.file)
    log = get_logger("cli.infer")

    log.info("Building model", model_type=cfg.model.model_type, model_id=cfg.model.model_id)
    model_obj = build_model(cfg.model.model_type, config=cfg)
    model_obj.load(checkpoint=checkpoint)
    model = model_obj.model
    processor = model_obj.processor
    device = model.device
    model.eval()

    log.info("Loading test dataset", language=cfg.dataset.language)
    test_ds = load_waxal_dataset(
        dataset_id=cfg.dataset.dataset_id,
        language=cfg.dataset.language,
        split="test",
        streaming=cfg.dataset.streaming,
        sample_rate=cfg.dataset.sample_rate,
        subset=num_samples,
    )

    ids: list[str] = []
    predictions: list[str] = []

    for batch in tqdm(test_ds.batch(batch_size=batch_size), desc="Inferring"):
        ids.extend(str(i) for i in range(len(batch.get("transcription", [1]))))
        preds = _transcribe_batch(batch, model, processor, device)
        predictions.extend(preds)

    df = pd.DataFrame({"ID": ids, "Target": predictions})
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    log.info("Predictions saved", path=str(output), rows=len(df))


def _transcribe_batch(
    batch: dict[str, list],
    model: torch.nn.Module,
    processor: Any,
    device: torch.device,
    max_new_tokens: int = 128,
) -> list[str]:
    messages_list = [msgs[:-1] for msgs in batch["messages"]]
    audio_list = [np.asarray(a["array"]).flatten() for a in batch["audio"]]

    text_prompts = processor.tokenizer.apply_chat_template(
        messages_list, add_generation_prompt=True, tokenize=False
    )
    inputs = processor(
        text=text_prompts,
        audio=audio_list,
        return_tensors="pt",
        padding=True,
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=processor.tokenizer.pad_token_id,
        )

    input_len = inputs.input_ids.shape[1]
    decoded = processor.tokenizer.batch_decode(outputs[:, input_len:], skip_special_tokens=True)
    return [t.strip() for t in decoded]


if __name__ == "__main__":
    app()
