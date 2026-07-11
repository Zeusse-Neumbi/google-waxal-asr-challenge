"""HuggingFace dataset loading for WaxalNLP.

Loads and formats the WaxalNLP dataset with streaming support and chat formatting.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import datasets

__all__ = ["load_waxal_dataset", "format_for_chat", "format_batch"]


def format_for_chat(
    example: Mapping[str, Any],
    system_message: str = "You are an assistant that transcribes speech accurately.",
    user_message: str = "Please transcribe this audio.",
) -> dict[str, Any]:
    """Converts a decoded example into a chat-formatted message list.

    Args:
        example: Dict with 'audio' (decoded) and 'transcription' keys.
        system_message: System prompt text.
        user_message: User prompt text.

    Returns:
        The example with an additional 'messages' key.
    """
    audio = example["audio"]
    audio_array = audio["array"]

    return {
        **example,
        "messages": [
            {
                "role": "system",
                "content": [{"type": "text", "text": system_message}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "audio", "audio": audio_array},
                    {"type": "text", "text": user_message},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": str(example["transcription"])}],
            },
        ],
    }


def format_batch(batch: dict[str, list[Any]]) -> dict[str, list[Any]]:
    """Formats a batch of decoded examples into chat messages."""
    num = len(batch["transcription"])
    examples = [{k: batch[k][i] for k in batch} for i in range(num)]
    formatted = [format_for_chat(ex) for ex in examples]
    return {k: [ex[k] for ex in formatted] for k in formatted[0]}


def load_waxal_dataset(
    dataset_id: str = "google/WaxalNLP",
    language: str = "sna",
    split: str = "train",
    streaming: bool = True,
    sample_rate: int = 16000,
    subset: int | None = None,
) -> datasets.Dataset | datasets.IterableDataset:
    """Load a WaxalNLP language split with streaming and chat formatting.

    When ``streaming=False``, data is still fetched via streaming internally (to avoid
    downloading the 27 GB ``unlabeled`` split that Colab disk cannot hold), then
    materialised into a regular :class:`datasets.Dataset` via ``Dataset.from_list``.
    This keeps disk usage proportional to ``subset`` (or the full split size if no
    subset), not the entire dataset config.

    Args:
        dataset_id: HuggingFace dataset identifier.
        language: Language code (e.g. 'sna', 'twi', 'hau').
        split: Dataset split ('train', 'validation', 'test').
        streaming: If True, return an IterableDataset. If False, return a regular
            Dataset (materialised from a stream — see note above).
        sample_rate: Target audio sample rate in Hz.
        subset: If set, take only this many examples (for quick testing).

    Returns:
        A formatted dataset (IterableDataset or Dataset) with 'messages' key added.
    """
    # Always stream from HF — avoids downloading the unlabeled split (~27 GB).
    ds: datasets.IterableDataset = datasets.load_dataset(
        dataset_id,
        name=f"{language}_asr",
        split=split,
        streaming=True,
    )

    if subset is not None:
        ds = ds.take(subset)

    ds = ds.cast_column("audio", datasets.Audio(sampling_rate=sample_rate))
    ds = ds.map(format_batch, batched=True, batch_size=32)

    if streaming:
        return ds

    # Materialise the stream into a regular Dataset for Seq2SeqTrainer compatibility.
    # This decodes audio in-memory; keep `subset` bounded to avoid OOM.
    return datasets.Dataset.from_list(list(ds))


def interleaved_shuffle(
    datasets_list: Sequence[datasets.IterableDataset],
    seed: int = 42,
) -> datasets.IterableDataset:
    """Interleave and shuffle multiple language datasets for multilingual training."""
    if len(datasets_list) == 1:
        return datasets_list[0]
    combined = datasets.interleave_datasets(datasets_list, seed=seed)
    return combined
