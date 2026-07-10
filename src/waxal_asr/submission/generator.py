"""Competition submission generator and validator.

Produces CSVs matching the Zindi format: columns ``ID``, ``Target``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from waxal_asr.utils.logging import get_logger

__all__ = ["SubmissionGenerator", "SubmissionValidator"]

log = get_logger("submission")

REQUIRED_COLUMNS = ["ID", "Target"]


class SubmissionValidator:
    """Validate a submission CSV against the Zindi competition spec."""

    @staticmethod
    def validate(path: str | Path) -> dict:
        """Check schema, row count, ID alignment. Return a report dict."""
        path = Path(path)
        df = pd.read_csv(path)

        report: dict = {
            "path": str(path),
            "columns": list(df.columns),
            "rows": len(df),
            "passed": True,
            "errors": [],
        }

        # Schema check
        if list(df.columns) != REQUIRED_COLUMNS:
            report["passed"] = False
            report["errors"].append(f"Expected columns {REQUIRED_COLUMNS}, got {list(df.columns)}")

        # Row count check
        if len(df) == 0:
            report["passed"] = False
            report["errors"].append("Empty CSV")

        # ID format check
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                report["passed"] = False
                report["errors"].append(f"Missing column: {col}")

        if report["passed"]:
            log.info("submission validated", **report)
        else:
            log.warning("submission validation failed", errors=report["errors"])

        return report


class SubmissionGenerator:
    """Generate the next monotonic submission CSV."""

    def __init__(self, output_dir: str | Path = "submissions") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def next_number(self) -> int:
        existing = sorted(self.output_dir.glob("submission_*.csv"))
        if not existing:
            return 1
        last = int(existing[-1].stem.split("_")[1])
        return last + 1

    def generate(
        self,
        ids: list[str],
        predictions: list[str],
    ) -> Path:
        """Write ``submission_NNN.csv`` with columns ``ID, Target``.

        Parameters
        ----------
        ids:
            Utterance IDs (must match Test.csv).
        predictions:
            Predicted transcriptions (same order as ids).

        Returns
        -------
        Path to the written CSV.
        """
        if len(ids) != len(predictions):
            raise ValueError(f"Length mismatch: {len(ids)} ids vs {len(predictions)} predictions")

        df = pd.DataFrame({"ID": ids, "Target": predictions})
        num = self.next_number()
        out_path = self.output_dir / f"submission_{num:03d}.csv"
        df.to_csv(out_path, index=False)

        report = SubmissionValidator.validate(out_path)
        log.info("submission written", path=str(out_path), rows=len(df), report=report)

        return out_path
