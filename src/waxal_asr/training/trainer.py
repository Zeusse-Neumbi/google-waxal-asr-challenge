"""Trainer orchestration — TRL-based fine-tuning loop.

Supports multiple model types (Gemma 3n, Whisper, etc.) via the ASRModel protocol
and model-specific data collators.
"""

from __future__ import annotations

from typing import Any

import torch
import trl

from waxal_asr.config.schemas import Config
from waxal_asr.data.collator import get_collator
from waxal_asr.data.dataset import load_waxal_dataset
from waxal_asr.metrics.text import normalize_corpus
from waxal_asr.utils.logging import get_logger
from waxal_asr.utils.seeding import seed_everything

__all__ = ["Trainer"]

log = get_logger("training.trainer")


class Trainer:
    """Fine-tuning orchestrator.

    Wraps TRL's SFTTrainer with model-agnostic config-driven setup.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def fit(self) -> None:
        cfg = self.config

        seed_everything(cfg.repro.seed, deterministic=cfg.repro.deterministic)

        # ------------------------------------------------------------------ #
        # 1. Load model + processor
        # ------------------------------------------------------------------ #
        log.info("Building model", model_type=cfg.model.model_type, model_id=cfg.model.model_id)
        model_obj = _build_model_protocol(cfg)
        model_obj.load()
        model = model_obj.model
        processor = model_obj.processor

        log.info("Model loaded", device=next(model.parameters()).device, dtype=str(model.dtype))

        # ------------------------------------------------------------------ #
        # 2. Load datasets
        # ------------------------------------------------------------------ #
        log.info("Loading train dataset", language=cfg.dataset.language)
        train_ds = load_waxal_dataset(
            dataset_id=cfg.dataset.dataset_id,
            language=cfg.dataset.language,
            split="train",
            streaming=cfg.dataset.streaming,
            sample_rate=cfg.dataset.sample_rate,
            subset=cfg.dataset.max_train_samples,
        )

        log.info("Loading validation dataset", language=cfg.dataset.language)
        val_ds = load_waxal_dataset(
            dataset_id=cfg.dataset.dataset_id,
            language=cfg.dataset.language,
            split="validation",
            streaming=cfg.dataset.streaming,
            sample_rate=cfg.dataset.sample_rate,
        )

        # Shuffle + repeat the training set for endless streaming
        shuffled_train = train_ds.shuffle(buffer_size=1000, seed=cfg.repro.seed).repeat(None)
        val_ds_fixed = val_ds.take(cfg.dataset.num_validation_examples)

        # ------------------------------------------------------------------ #
        # 3. Collator
        # ------------------------------------------------------------------ #
        collator = get_collator(
            cfg.model.model_type, processor, max_length=cfg.training.max_seq_length
        )

        # ------------------------------------------------------------------ #
        # 4. LoRA config
        # ------------------------------------------------------------------ #
        lora_config = None
        if cfg.lora.enabled:
            import peft

            lora_config = peft.LoraConfig(
                task_type="CAUSAL_LM",
                r=cfg.lora.r,
                lora_alpha=cfg.lora.alpha,
                lora_dropout=cfg.lora.dropout,
                target_modules=list(cfg.lora.target_modules),
                bias=cfg.lora.bias,
                use_rslora=cfg.lora.use_rslora,
                use_dora=cfg.lora.use_dora,
            )

        # ------------------------------------------------------------------ #
        # 5. TRL SFTConfig
        # ------------------------------------------------------------------ #
        import trl

        training_args = trl.SFTConfig(
            output_dir=str(cfg.paths.outputs / f"gemma3n-asr-{cfg.dataset.language}"),
            max_steps=cfg.training.max_steps,
            eval_strategy=cfg.training.eval_strategy,
            eval_steps=cfg.training.eval_steps,
            per_device_train_batch_size=cfg.training.per_device_train_batch_size,
            per_device_eval_batch_size=cfg.training.per_device_eval_batch_size,
            gradient_accumulation_steps=cfg.training.gradient_accumulation_steps,
            gradient_checkpointing=cfg.training.gradient_checkpointing,
            gradient_checkpointing_kwargs={"use_reentrant": False},
            learning_rate=cfg.optimizer.lr,
            logging_steps=cfg.training.logging_steps,
            save_steps=cfg.training.save_steps,
            save_total_limit=cfg.training.save_total_limit,
            bf16=torch.cuda.is_bf16_supported(),
            fp16=not torch.cuda.is_bf16_supported(),
            report_to=cfg.training.report_to,
            run_name=cfg.training.run_name or f"gemma3n-asr-{cfg.dataset.language}",
            dataset_kwargs={"skip_prepare_dataset": True},
            remove_unused_columns=cfg.training.remove_unused_columns,
            max_length=cfg.training.max_seq_length,
            packing=cfg.training.packing,
            dataloader_num_workers=cfg.training.dataloader_num_workers,
            seed=cfg.repro.seed,
        )

        # ------------------------------------------------------------------ #
        # 6. SFTTrainer
        # ------------------------------------------------------------------ #
        trainer = _PatchedSFTTrainer(
            model=model,
            args=training_args,
            data_collator=collator,
            train_dataset=shuffled_train,
            eval_dataset=val_ds_fixed,
            peft_config=lora_config,
        )

        log.info("Starting training …")
        trainer.train()  # type: ignore[attr-defined]
        log.info("Training complete.")

        # ------------------------------------------------------------------ #
        # 7. Save adapter
        # ------------------------------------------------------------------ #
        save_path = str(cfg.paths.outputs / "adapter")
        model_obj.save(save_path)
        log.info("Adapter saved", path=save_path)

        # ------------------------------------------------------------------ #
        # 8. Evaluate on test set
        # ------------------------------------------------------------------ #
        log.info("Loading test dataset for evaluation")
        test_ds = load_waxal_dataset(
            dataset_id=cfg.dataset.dataset_id,
            language=cfg.dataset.language,
            split="test",
            streaming=cfg.dataset.streaming,
            sample_rate=cfg.dataset.sample_rate,
        )
        metrics = self._evaluate(model_obj, test_ds, cfg)
        log.info("Evaluation results", **metrics)

    def _evaluate(
        self,
        model_obj: Any,
        test_ds: Any,
        cfg: Config,
        num_samples: int = 200,
        batch_size: int = 4,
    ) -> dict[str, float]:
        """Run WER/CER evaluation on a test dataset using the model."""
        model = model_obj.model
        processor = model_obj.processor
        device = model.device
        model.eval()

        references: list[str] = []
        predictions: list[str] = []

        test_subset = test_ds.take(num_samples)
        for batch in test_subset.batch(batch_size=batch_size):
            preds = _transcribe_batch(batch, model, processor, device)
            references.extend(str(r) for r in batch["transcription"])
            predictions.extend(preds)

        refs_norm = normalize_corpus(references)
        preds_norm = normalize_corpus(predictions)

        from waxal_asr.metrics.wer import cer as _cer
        from waxal_asr.metrics.wer import wer as _wer

        return {
            "wer": _wer(refs_norm, preds_norm),
            "cer": _cer(refs_norm, preds_norm),
        }


def _transcribe_batch(
    batch: dict[str, list[Any]],
    model: torch.nn.Module,
    processor: Any,
    device: torch.device,
    max_new_tokens: int = 128,
) -> list[str]:
    """Run inference on a batch and return decoded transcriptions."""
    messages_list = [msgs[:-1] for msgs in batch["messages"]]
    audio_list = [__import__("numpy").asarray(a["array"]).flatten() for a in batch["audio"]]

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


def _build_model_protocol(config: Config) -> Any:
    """Build a model instance from config using the registry."""
    from waxal_asr.models.registry import build_model

    return build_model(config.model.model_type, config=config)


class _PatchedSFTTrainer:
    """SFTTrainer subclass that patches create_model_card to avoid importlib issues."""

    def __new__(cls, *args: Any, **kwargs: Any) -> trl.SFTTrainer:
        class _Trainer(trl.SFTTrainer):
            def create_model_card(
                self,
                model_name: str | None = None,
                dataset_name: str | None = None,
                tags: str | list[str] | None = None,
            ) -> None:
                pass

        return _Trainer(*args, **kwargs)
