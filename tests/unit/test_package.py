"""Sanity test for package import + version."""

import waxal_asr


def test_package_importable() -> None:
    assert waxal_asr is not None


def test_version_string() -> None:
    assert isinstance(waxal_asr.__version__, str)
    assert waxal_asr.__version__.count(".") >= 1
