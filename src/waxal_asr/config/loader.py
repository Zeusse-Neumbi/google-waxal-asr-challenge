"""Config loader.

Loads YAML configs (with OmegaConf-style `${...}` interpolation and `defaults` inheritance)
into the typed `Config` schema defined in `schemas.py`.

Usage:
    from waxal_asr.config import load_config
    cfg = load_config("configs/baseline.yaml")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from waxal_asr.config.schemas import Config

__all__ = ["load_config", "load_yaml"]


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a single YAML file into a dict."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def _interpolate(value: Any, context: dict[str, Any]) -> Any:
    """Recursively resolve `${a.b.c}` references against `context`."""
    if isinstance(value, str):
        if "${" in value:
            # Simple interpolation: replace each ${path.to.key} with context value.
            for _ in range(10):  # bounded resolution depth
                if "${" not in value:
                    break
                start = value.find("${")
                end = value.find("}", start)
                if end == -1:
                    break
                key = value[start + 2 : end]
                parts = key.split(".")
                ref: Any = context
                for part in parts:
                    if isinstance(ref, dict) and part in ref:
                        ref = ref[part]
                    else:
                        ref = value[start : end + 1]
                        break
                else:
                    value = value[:start] + str(ref) + value[end + 1 :]
        return value
    if isinstance(value, dict):
        return {k: _interpolate(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [_interpolate(v, context) for v in value]
    return value


def _resolve_defaults(data: dict[str, Any], config_dir: Path) -> dict[str, Any]:
    """Merge `defaults: [name1, name2]` entries (parent configs) into `data`."""
    defaults = data.pop("defaults", []) or []
    merged: dict[str, Any] = {}
    for name in defaults:
        parent_path = config_dir / f"{name}.yaml"
        parent = load_yaml(parent_path)
        parent = _resolve_defaults(parent, config_dir)
        merged = _deep_merge(merged, parent)
    merged = _deep_merge(merged, data)
    return merged


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge `override` into `base` (override wins)."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def load_config(path: str | Path) -> Config:
    """Load a YAML config (with inheritance + interpolation) into a `Config` object."""
    path = Path(path)
    config_dir = path.parent
    data = load_yaml(path)
    data = _resolve_defaults(data, config_dir)
    data = _interpolate(data, data)
    return _build_config(data)


def _build_config(data: dict[str, Any]) -> Config:
    """Construct a `Config` from a fully-resolved dict, keeping the raw dict too."""
    import typing
    from dataclasses import fields, is_dataclass

    def build(cls: type, d: dict[str, Any]) -> Any:
        # Resolve string annotations (when `from __future__ import annotations` is used)
        # to actual types so we can recurse into nested dataclasses.
        hints = typing.get_type_hints(cls)
        kwargs: dict[str, Any] = {}
        for f in fields(cls):
            if f.name not in d:
                continue
            val = d[f.name]
            ftype = hints.get(f.name, f.type)
            if is_dataclass(ftype) and isinstance(val, dict):
                kwargs[f.name] = build(ftype, val)
            else:
                # Coerce Path-typed fields from str.
                if ftype is Path and isinstance(val, str):
                    val = Path(val)
                kwargs[f.name] = val
        return cls(**kwargs)

    cfg: Config = build(Config, data)
    cfg.raw = data
    return cfg
