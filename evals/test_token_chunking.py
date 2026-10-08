"""Synthetic checks for the diagnostic splitter, not a production change."""
import pytest
from tokenizers import Tokenizer

from outwise.knowledge.models import KnowledgeItem
from compare_token_chunking import ROOT, split_item


@pytest.mark.parametrize("text", [
    "Short text.",
    "This is a long source sentence containing instructions and a condition. " * 40,
    "Step one.\nStep two is conditional.\n" * 35,
    "A single very long sentence without punctuation or paragraph breaks " * 40,
])
def test_split_is_lossless_and_fits_both_views(text):
    tokenizer = Tokenizer.from_file(str(ROOT / "knowledge/local/embedding-model/tokenizer.json"))
    tokenizer.no_padding()
    tokenizer.no_truncation()
    item = KnowledgeItem(id="test", text=text, title="Title", source_name="Synthetic",
                         source_url="https://example.test", license="synthetic", language="en",
                         topic="Test", section="Test section", metadata={"jurisdiction": "general"})
    children, spans = split_item(item, tokenizer, 128)
    assert "".join(child.text for child in children) == text
    assert all(s["context_tokens"] <= 128 and s["text_tokens"] <= 128 for s in spans)
    assert all(child.metadata == item.metadata and child.section == item.section for child in children)
    assert spans[0]["start"] == 0 and spans[-1]["end"] == len(text)
    assert all(left["end"] == right["start"] for left, right in zip(spans, spans[1:]))
