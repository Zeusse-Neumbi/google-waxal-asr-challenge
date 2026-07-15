"""Unit tests for the streaming multilingual Trainer."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from waxal_asr.config import load_config
from waxal_asr.training.trainer import Trainer

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_whisper_config() -> object:
    """Load the shipped whisper-small.yaml as a realistic Config."""
    return load_config(_REPO_ROOT / "configs" / "whisper-small.yaml")


class TestTrainerModuleImport:
    """Verify the trainer module imports cleanly — no trl dependency."""

    @pytest.mark.unit
    def test_module_imports_cleanly(self) -> None:
        import importlib

        mod = importlib.import_module("waxal_asr.training.trainer")
        assert mod is not None
        assert hasattr(mod, "Trainer")

    @pytest.mark.unit
    def test_trl_not_imported(self) -> None:
        """Trainer no longer imports trl at all."""
        assert "trl" not in sys.modules


class TestTrainerInit:
    @pytest.mark.unit
    def test_trainer_stores_config(self) -> None:
        cfg = _load_whisper_config()
        trainer = Trainer(cfg)
        assert trainer.config is cfg


class TestTrainerFitDispatchesCorrectly:
    """Verify fit() calls all expected sub-components."""

    @pytest.mark.unit
    def test_fit_calls_all_components(self) -> None:
        cfg = _load_whisper_config()

        with (
            patch("waxal_asr.training.trainer.seed_everything") as mock_seed,
            patch("waxal_asr.training.trainer._build_model") as mock_build,
            patch.object(Trainer, "_build_train_stream") as mock_train_stream,
            patch.object(Trainer, "_build_val_stream") as mock_val_stream,
            patch.object(Trainer, "_build_optimizer") as mock_opt,
            patch.object(Trainer, "_build_scheduler") as mock_sched,
            patch.object(Trainer, "_evaluate") as mock_eval,
        ):
            mock_model = MagicMock()
            mock_model.model = MagicMock()
            mock_model.model.parameters.side_effect = lambda: iter([MagicMock()])
            mock_model.model.dtype = "float16"
            mock_build.return_value = mock_model

            mock_train_stream.return_value.batch.return_value = []
            mock_val_stream.return_value.take.return_value = []
            mock_opt.return_value = MagicMock()
            mock_sched.return_value = MagicMock()

            trainer = Trainer(cfg)
            trainer.fit()

            mock_seed.assert_called_once_with(cfg.repro.seed, deterministic=cfg.repro.deterministic)
            mock_build.assert_called_once_with(cfg)
            mock_model.load.assert_called_once()
            mock_train_stream.assert_called_once()
            mock_val_stream.assert_called_once()
            mock_opt.assert_called_once()
            mock_sched.assert_called_once()
            mock_model.save.assert_called_once()  # final save
            mock_eval.assert_called_once()  # final eval


class TestBuildTrainStream:
    @pytest.mark.unit
    def test_single_language_skips_interleaved_shuffle(self) -> None:
        cfg = _load_whisper_config()
        trainer = Trainer(cfg)

        with (
            patch("waxal_asr.training.trainer.load_waxal_dataset") as mock_load,
            patch("waxal_asr.training.trainer.interleaved_shuffle") as mock_interleave,
        ):
            mock_ds = MagicMock()
            mock_ds.shuffle.return_value = mock_ds
            mock_ds.repeat.return_value = mock_ds
            mock_load.return_value = mock_ds

            trainer._build_train_stream(["sna"], cfg)

            assert mock_load.call_count == 1
            mock_interleave.assert_not_called()
            mock_ds.shuffle.assert_called_once()
            mock_ds.repeat.assert_called_once_with(None)

    @pytest.mark.unit
    def test_multilingual_calls_interleaved_shuffle(self) -> None:
        cfg = _load_whisper_config()
        trainer = Trainer(cfg)

        with (
            patch("waxal_asr.training.trainer.load_waxal_dataset") as mock_load,
            patch("waxal_asr.training.trainer.interleaved_shuffle") as mock_interleave,
        ):
            mock_ds = MagicMock()
            mock_load.return_value = mock_ds
            mock_interleave.return_value = mock_ds
            mock_ds.shuffle.return_value = mock_ds
            mock_ds.repeat.return_value = mock_ds

            trainer._build_train_stream(["lin", "sna", "lug"], cfg)

            assert mock_load.call_count == 3
            mock_interleave.assert_called_once()


class TestLanguagesFallback:
    @pytest.mark.unit
    def test_languages_none_falls_back_to_language(self) -> None:
        cfg = _load_whisper_config()
        cfg.dataset.languages = None
        cfg.dataset.language = "twi"

        trainer = Trainer(cfg)

        with (
            patch("waxal_asr.training.trainer.seed_everything"),
            patch("waxal_asr.training.trainer._build_model") as mock_build,
            patch.object(Trainer, "_build_train_stream") as mock_train_stream,
            patch.object(Trainer, "_build_val_stream"),
            patch.object(Trainer, "_build_optimizer"),
            patch.object(Trainer, "_build_scheduler"),
            patch.object(Trainer, "_evaluate") as mock_eval,
        ):
            mock_model = MagicMock()
            mock_model.model = MagicMock()
            mock_model.model.parameters.side_effect = lambda: iter([MagicMock()])
            mock_model.model.dtype = "float16"
            mock_build.return_value = mock_model

            mock_train_stream.return_value.batch.return_value = []
            mock_eval.return_value = {}

            trainer.fit()

            mock_train_stream.assert_called_once_with(["twi"], cfg)


class TestEvaluate:
    @pytest.mark.unit
    def test_evaluate_computes_wer_cer(self) -> None:
        cfg = _load_whisper_config()
        cfg.dataset.num_validation_examples = 3
        trainer = Trainer(cfg)

        mock_model = MagicMock()
        mock_model.model = MagicMock()

        # Return predictable transcriptions
        mock_model.transcribe.side_effect = [
            "hello world",
            "good morning",
            "good afternoon",
        ]

        # Mock val_stream as a list of dicts (take() already returns a list in mock)
        mock_stream = MagicMock()
        mock_stream.take.return_value = [
            {
                "audio": {"array": [0.1, 0.2], "sampling_rate": 16000},
                "transcription": "hello world",
            },
            {
                "audio": {"array": [0.1, 0.2], "sampling_rate": 16000},
                "transcription": "good morning",
            },
            {
                "audio": {"array": [0.1, 0.2], "sampling_rate": 16000},
                "transcription": "good evening",  # deliberate mismatch
            },
        ]

        metrics = trainer._evaluate(mock_model, mock_stream, cfg)

        assert "wer" in metrics
        assert "cer" in metrics
        # Exact match on 2/3, one word wrong — WER > 0
        assert metrics["wer"] > 0.0
        # All in [0, 1] range
        assert 0.0 <= metrics["wer"] <= 1.0
        assert 0.0 <= metrics["cer"] <= 1.0
