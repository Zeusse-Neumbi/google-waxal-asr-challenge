"""Train-only audio augmentations: SpecAugment, noise, speed perturbation.

Augmentations are NEVER applied to dev/test data.
"""

from waxal_asr.data.augmentation.noise import add_noise
from waxal_asr.data.augmentation.specaugment import spec_augment
from waxal_asr.data.augmentation.speed import speed_perturb

__all__ = ["add_noise", "spec_augment", "speed_perturb"]
