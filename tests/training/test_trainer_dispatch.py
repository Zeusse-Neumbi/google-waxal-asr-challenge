"""Unit tests for Trainer.fit() model-type dispatch (mocked — no training runs)."""

from __future__ import annotations

import importlib
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


@pytest.fixture
def _patch_seed() -> object:
    """Avoid side effects from seed_everything during dispatch tests."""
    with patch("waxal_asr.training.trainer.seed_everything") as mock_seed:
        yield mock_seed


class TestTrainerDispatch:
    @pytest.mark.unit
    def test_gemma3n_dispatches_to_fit_gemma(self, _patch_seed: object) -> None:
        cfg = _load_whisper_config()
        cfg.model.model_type = "gemma3n"

        trainer = Trainer(cfg)
        trainer._fit_gemma = MagicMock()
        trainer._fit_whisper = MagicMock()

        trainer.fit()

        trainer._fit_gemma.assert_called_once_with()
        trainer._fit_whisper.assert_not_called()

    @pytest.mark.unit
    def test_whisper_dispatches_to_fit_whisper(self, _patch_seed: object) -> None:
        cfg = _load_whisper_config()
        assert cfg.model.model_type == "whisper"

        trainer = Trainer(cfg)
        trainer._fit_gemma = MagicMock()
        trainer._fit_whisper = MagicMock()

        trainer.fit()

        trainer._fit_whisper.assert_called_once_with()
        trainer._fit_gemma.assert_not_called()

    @pytest.mark.unit
    def test_unknown_model_type_raises(self, _patch_seed: object) -> None:
        cfg = _load_whisper_config()
        cfg.model.model_type = "unknown"

        trainer = Trainer(cfg)
        trainer._fit_gemma = MagicMock()
        trainer._fit_whisper = MagicMock()

        with pytest.raises(ValueError, match="Unsupported model_type"):
            trainer.fit()

        trainer._fit_gemma.assert_not_called()
        trainer._fit_whisper.assert_not_called()

    @pytest.mark.unit
    def test_seed_everything_called_with_config(self, _patch_seed: object) -> None:
        cfg = _load_whisper_config()
        trainer = Trainer(cfg)
        trainer._fit_whisper = MagicMock()

        trainer.fit()

        _patch_seed.assert_called_once_with(cfg.repro.seed, deterministic=cfg.repro.deterministic)


class TestTrainerModuleImport:
    """Verify the trainer module imports without pulling in trl (lazy import)."""

    @pytest.mark.unit
    def test_module_imports_cleanly(self) -> None:
        mod = importlib.import_module("waxal_asr.training.trainer")
        assert mod is not None
        assert hasattr(mod, "Trainer")

    @pytest.mark.unit
    def test_trl_not_imported_at_module_level(self) -> None:
        """Importing the trainer module must not trigger `import trl`."""
        # Remove trl from cache so we detect if importing the module pulls it in.
        had_trl = sys.modules.pop("trl", None)
        try:
            # Also remove the trainer module so it re-imports fresh.
            sys.modules.pop("waxal_asr.training.trainer", None)
            importlib.import_module("waxal_asr.training.trainer")
            assert (
                "trl" not in sys.modules
            ), "trl was imported at module level — it must be lazy (inside _fit_gemma)"
        finally:
            # Restore original state.
            if had_trl is not None:
                sys.modules["trl"] = had_trl
