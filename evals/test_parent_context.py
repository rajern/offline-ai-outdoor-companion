"""Synthetic packet integrity/budget tests for the isolated experiment."""
from outwise.knowledge.models import KnowledgeItem
from compare_parent_context import pack, packet_members


def item(id, section="Heading", document="doc", jurisdiction="general"):
    return KnowledgeItem(id=id, text=f"Entire original text for {id}.", title="Test",
                         source_name="Synthetic", source_url="https://example.test", license="synthetic",
                         language="en", topic=section, section=section, document_id=document,
                         metadata={"jurisdiction": jurisdiction, "is_location_specific": jurisdiction != "general"})


def seed(child, parent, rank):
    return {"rank": rank, "item": child, "parent_id": parent.id, "score": .9 - rank / 100,
            "span": {"id": child.id, "parent_id": parent.id, "start": 0, "end": 5}}


class Counter:
    def count(self, prompt):
        return len(prompt), "fake"


def test_section_expansion_preserves_document_and_geography():
    a, b = item("a", "Heading / Child"), item("b", "Heading")
    foreign, other = item("foreign", "Heading", jurisdiction="NZ"), item("other", "Heading", document="another-doc")
    parents = {i.id: i for i in [a, b, foreign, other]}
    assert [i.id for i in packet_members(a, "section_unique", parents)] == ["a", "b"]


def test_restore_deduplicates_without_refill_and_preserves_full_text():
    a, b = item("a"), item("b")
    seeds = [seed(item("a1"), a, 1), seed(item("a2"), a, 2), seed(item("b1"), b, 3)]
    restored = pack("Question", seeds, "parent_restore", 2, {"a": a, "b": b}, Counter(), 10000)
    unique = pack("Question", seeds, "parent_unique", 2, {"a": a, "b": b}, Counter(), 10000)
    assert [r["item"]["id"] for r in restored["excerpts"]] == ["a"]
    assert restored["excerpts"][0]["item"]["text"] == a.text
    assert [r["item"]["id"] for r in unique["excerpts"]] == ["a", "b"]


def test_budget_never_truncates_or_includes_over_budget_packet():
    a, b = item("a"), item("b", "Other")
    parents = {"a": a, "b": b}
    seeds = [seed(item("a1"), a, 1), seed(item("b1"), b, 2)]
    full = pack("Question", seeds, "parent_unique", 1, parents, Counter(), 10000)
    bounded = pack("Question", seeds, "parent_unique", 2, parents, Counter(), full["prompt_tokens"])
    assert len(bounded["excerpts"]) == 1
    assert bounded["excerpts"][0]["item"]["text"] == a.text
    assert any(t["status"] == "over_budget" for t in bounded["trace"])


def test_duplicate_section_root_does_not_repeat_original_parent_text():
    a, b, c = item("a", "Heading"), item("b", "Heading / Subsection"), item("c", "Other")
    parents = {i.id: i for i in [a, b, c]}
    seeds = [seed(item("a1"), a, 1), seed(item("b1"), b, 2), seed(item("c1"), c, 3)]
    result = pack("Question", seeds, "section_unique", 2, parents, Counter(), 10000)
    assert [r["item"]["id"] for r in result["excerpts"]] == ["a", "b", "c"]
    assert len(result["packets"]) == 2
