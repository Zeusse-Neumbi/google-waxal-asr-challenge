"""Submission generation and validation for the Zindi competition.

Produces CSVs in the Zindi format: columns ``ID``, ``Target``.
"""

from waxal_asr.submission.generator import SubmissionGenerator, SubmissionValidator

__all__ = ["SubmissionGenerator", "SubmissionValidator"]
