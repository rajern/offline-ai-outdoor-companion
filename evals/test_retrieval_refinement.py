"""Synthetic checks; no query-specific clinical rules or production edits."""
from outwise.knowledge.models import KnowledgeItem
from compare_retrieval_refinement import BM25, narrow_members, rank_parents


def item(id, section, document="doc", jurisdiction="general"):
    return KnowledgeItem(id=id, text=f"Text for {id}", title="Test", section=section, topic=section,
                         source_name="Synthetic", source_url="https://example.test", license="synthetic", language="en",
                         document_id=document, metadata={"jurisdiction": jurisdiction, "is_location_specific": jurisdiction != "general"})


def test_narrow_branch_excludes_other_root_branches_and_foreign_content():
    nodes = [item("root", "Prevention"), item("treatment", "Prevention / Treatment"),
             item("boil", "Prevention / Treatment / Boil"), item("hygiene", "Prevention / Hygiene"),
             item("foreign", "Prevention / Treatment / Extra", jurisdiction="NZ"), item("another", "Prevention / Treatment", document="other")]
    parents = {node.id: node for node in nodes}
    assert [i.id for i in narrow_members(nodes[1], parents)[1]] == ["treatment", "boil"]
    assert [i.id for i in narrow_members(nodes[2], parents)[1]] == ["treatment", "boil"]
    assert [i.id for i in narrow_members(nodes[0], parents)[1]] == ["root"]


def test_single_branch_preserves_definition_and_instruction_continuations():
    nodes = [item("definition", "Injury"), item("instructions", "Injury / First aid"), item("continuation", "Injury / First aid / Details")]
    parents = {node.id: node for node in nodes}
    assert [i.id for i in narrow_members(nodes[0], parents)[1]] == ["definition", "instructions", "continuation"]
    assert [i.id for i in narrow_members(nodes[1], parents)[1]] == ["instructions", "continuation"]


def test_hybrid_cannot_bypass_cosine_gate_and_zero_lexical_preserves_order():
    nodes = [item("a", "A"), item("b", "B"), item("c", "C")]
    parents = {node.id: node for node in nodes}
    spans = {node.id: {"parent_id": node.id} for node in nodes}
    semantic, hybrid, _ = rank_parents(parents, nodes, spans, [.8, .7, .3], {"a": 0, "b": 0, "c": 100})
    assert [s["parent_id"] for s in semantic] == ["a", "b"]
    assert [s["parent_id"] for s in hybrid] == ["a", "b"]


def test_bm25_excludes_foreign_and_positive_match_is_observable():
    a, b, foreign = item("river", "River warning signs"), item("tree", "Trees"), item("foreign", "River", jurisdiction="NZ")
    scores = BM25({node.id: node for node in [a, b, foreign]}).score("What river warning signs matter?")
    assert scores["river"] > scores["tree"] == 0
    assert "foreign" not in scores
