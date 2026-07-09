"""Model registry.

Maps `model.name` (from config) to a factory. New models register here.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from waxal_asr.models.base import ASRModel

__all__ = ["build_model", "register_model"]

_REGISTRY: dict[str, Callable[..., ASRModel]] = {}


def register_model(name: str) -> Callable[[Callable[..., ASRModel]], Callable[..., ASRModel]]:
    """Decorator to register a model factory under `name`."""

    def decorator(factory: Callable[..., ASRModel]) -> Callable[..., ASRModel]:
        if name in _REGISTRY:
            raise ValueError(f"Model already registered: {name}")
        _REGISTRY[name] = factory
        return factory

    return decorator


def build_model(name: str, **kwargs: Any) -> ASRModel:
    """Construct a model by name from the registry."""
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown model '{name}'. Registered: {sorted(_REGISTRY)}. "
            "Add it via @register_model in waxal_asr.models.registry."
        )
    return _REGISTRY[name](**kwargs)
