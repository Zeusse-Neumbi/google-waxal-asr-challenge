"""Streaming trainer — model-agnostic, true streaming, multilingual.

One unified training loop that works for any model implementing the ASRModel
protocol (Whisper, Gemma, etc.). Iterates an IterableDataset directly —
only one batch in RAM at a time. Supports multilingual training by interleaving
language-specific dataset streams.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import torch

from waxal_asr.config.schemas import Config
from waxal_asr.data.collator import get_collator
from waxal_asr.data.dataset import interleaved_shuffle, load_waxal_dataset
from waxal_asr.metrics.text import normalize_corpus
from waxal_asr.metrics.wer import cer as _cer
from waxal_asr.metrics.wer import wer as _wer
from waxal_asr.utils.logging import get_logger
from waxal_asr.utils.seeding import seed_everything

__all__ = ["Trainer"]

log = get_logger("training.trainer")


class Trainer:
    """Model-agnostic streaming trainer.

    Works with any ASRModel (Whisper, Gemma, etc.) via the ASRModel protocol.
    Supports multilingual training by interleaving language-specific streams.
    True streaming — only one batch in RAM at a time, no dataset materialisation.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def fit(self) -> None:
        """Run streaming fine-tuning on the configured model + languages."""
        cfg = self.config
        seed_everything(cfg.repro.seed, deterministic=cfg.repro.deterministic)

        # -- Languages ----------------------------------------------------- #
        languages = cfg.dataset.languages or [cfg.dataset.language]
        log.info("Training languages", languages=languages)

        # -- 1. Build model + processor ----------------------------------- #
        log.info("Building model", model_type=cfg.model.model_type, model_id=cfg.model.model_id)
        model_obj = _build_model(cfg)
        model_obj.load()
        model = model_obj.model
        processor = model_obj.processor
        device = next(model.parameters()).device
        log.info("Model loaded", device=device, dtype=str(model.dtype))

        # -- 2. Build multilingual streaming datasets ---------------------- #
        log.info("Building training stream")
        train_stream = self._build_train_stream(languages, cfg)
        log.info("Building validation stream")
        val_stream = self._build_val_stream(languages, cfg)

        # -- 3. Collator --------------------------------------------------- #
        collator = get_collator(
            cfg.model.model_type, processor, max_length=cfg.training.max_seq_length
        )

        # -- 4. Optimizer + scheduler -------------------------------------- #
        optimizer = self._build_optimizer(model, cfg)
        scheduler = self._build_scheduler(optimizer, cfg)

        # -- 5. Training loop ---------------------------------------------- #
        model.train()
        batch_size = cfg.training.per_device_train_batch_size
        accum_steps = cfg.training.gradient_accumulation_steps
        max_steps = cfg.training.max_steps
        global_step = 0
        accum_loss = 0.0

        log.info(
            "Starting streaming training",
            max_steps=max_steps,
            batch_size=batch_size,
            accum_steps=accum_steps,
        )

        for batch_count, raw_batch in enumerate(train_stream.batch(batch_size=batch_size), start=1):
            # Convert HF dict-of-lists to list-of-dicts for the collator
            batch_len = len(next(iter(raw_batch.values())))
            examples = [{k: raw_batch[k][i] for k in raw_batch} for i in range(batch_len)]
            tensor_batch = collator(examples)
            tensor_batch = {
                k: v.to(device) if isinstance(v, torch.Tensor) else v
                for k, v in tensor_batch.items()
            }

            # Forward + backward
            outputs = model(**tensor_batch)
            loss = outputs.loss / accum_steps
            loss.backward()
            accum_loss += loss.item()

            # Optimizer step (every accum_steps batches)
            if batch_count % accum_steps == 0:
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1

                # Logging
                if global_step % cfg.training.logging_steps == 0:
                    avg_loss = accum_loss / accum_steps
                    log.info(
                        "train",
                        step=global_step,
                        loss=f"{avg_loss:.4f}",
                        lr=f"{scheduler.get_last_lr()[0]:.2e}",
                    )
                    accum_loss = 0.0

                # Evaluation
                if global_step % cfg.training.eval_steps == 0:
                    metrics = self._evaluate(model_obj, val_stream, cfg)
                    log.info("eval", step=global_step, **metrics)
                    model.train()

                # Checkpoint
                if global_step % cfg.training.save_steps == 0:
                    save_path = str(
                        cfg.paths.outputs
                        / f"{cfg.model.model_type}-asr-multilingual"
                        / f"checkpoint-{global_step}"
                    )
                    model_obj.save(save_path)
                    log.info("checkpoint saved", path=save_path)

                if global_step >= max_steps:
                    break

        # -- 6. Final save ------------------------------------------------- #
        final_path = str(cfg.paths.outputs / f"{cfg.model.model_type}-asr-multilingual" / "final")
        model_obj.save(final_path)
        log.info("Training complete. Model saved.", path=final_path)

        # -- 7. Final evaluation ------------------------------------------- #
        metrics = self._evaluate(model_obj, val_stream, cfg)
        log.info("Final evaluation", **metrics)

    def _build_train_stream(self, languages: list[str], cfg: Config) -> Any:
        """Build an interleaved, shuffled, repeated training stream."""
        lang_streams = []
        for lang in languages:
            ds = load_waxal_dataset(
                dataset_id=cfg.dataset.dataset_id,
                language=lang,
                split="train",
                streaming=True,
                sample_rate=cfg.dataset.sample_rate,
                subset=cfg.dataset.max_train_samples,
            )
            lang_streams.append(ds)

        if len(lang_streams) == 1:
            combined = lang_streams[0]
        else:
            combined = interleaved_shuffle(lang_streams, seed=cfg.repro.seed)

        return combined.shuffle(buffer_size=1000, seed=cfg.repro.seed).repeat(None)

    def _build_val_stream(self, languages: list[str], cfg: Config) -> Any:
        """Build an interleaved validation stream."""
        lang_streams = []
        for lang in languages:
            ds = load_waxal_dataset(
                dataset_id=cfg.dataset.dataset_id,
                language=lang,
                split="validation",
                streaming=True,
                sample_rate=cfg.dataset.sample_rate,
            )
            lang_streams.append(ds)

        if len(lang_streams) == 1:
            return lang_streams[0]
        return interleaved_shuffle(lang_streams, seed=cfg.repro.seed)

    def _evaluate(
        self,
        model_obj: Any,
        val_stream: Any,
        cfg: Config,
    ) -> dict[str, float]:
        """Model-agnostic evaluation: transcribe N samples, compute WER/CER.

        Uses model_obj.transcribe() (ASRModel protocol) — works for any model.
        """
        num = cfg.dataset.num_validation_examples
        model_obj.model.eval()

        refs: list[str] = []
        preds: list[str] = []

        for ex in val_stream.take(num):
            audio_array = np.asarray(ex["audio"]["array"]).flatten()
            audio_tensor = torch.from_numpy(audio_array)
            sr = ex["audio"]["sampling_rate"]

            text = model_obj.transcribe(audio_tensor, sr, max_new_tokens=128)
            refs.append(str(ex["transcription"]))
            preds.append(text)

        refs_norm = normalize_corpus(refs)
        preds_norm = normalize_corpus(preds)

        return {
            "wer": _wer(refs_norm, preds_norm),
            "cer": _cer(refs_norm, preds_norm),
        }

    def _build_optimizer(self, model: torch.nn.Module, cfg: Config) -> torch.optim.Optimizer:
        """Build optimizer from config."""
        from torch.optim import AdamW

        return AdamW(
            model.parameters(),
            lr=cfg.optimizer.lr,
            weight_decay=cfg.optimizer.weight_decay,
            betas=cfg.optimizer.betas,
            eps=cfg.optimizer.eps,
        )

    def _build_scheduler(self, optimizer: torch.optim.Optimizer, cfg: Config) -> Any:
        """Build LR scheduler from config."""
        from transformers import get_scheduler

        num_warmup = int(cfg.training.max_steps * cfg.scheduler.warmup_ratio)
        return get_scheduler(
            name=cfg.scheduler.name,
            optimizer=optimizer,
            num_warmup_steps=num_warmup,
            num_training_steps=cfg.training.max_steps,
        )


def _build_model(config: Config) -> Any:
    """Build a model instance from config using the registry."""
    from waxal_asr.models.registry import build_model

    return build_model(config.model.model_type, config=config)
