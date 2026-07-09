"""Configuration system: load YAML configs, validate, and merge into typed dataclasses."""

from waxal_asr.config.loader import load_config
from waxal_asr.config.schemas import Config

__all__ = ["Config", "load_config"]
