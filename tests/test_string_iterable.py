"""Check that the string iterable loader is working as expected."""
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.parent)

from llama_hub.string_iterable.base import StringIterableReader


def test_string_iterable() -> None:
    """Check that StringIterableReader works correctly."""
    reader = StringIterableReader()
    documents = reader.load_data(texts=["I went to the store", "I bought an apple"])
    assert len(documents) == 2
