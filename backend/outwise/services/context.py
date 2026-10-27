"""Source-preserving P3 packing, ported from the measured retrieval candidate."""
from outwise.knowledge.models import RetrievedKnowledgeItem
from outwise.services.orchestrator import _build_grounded_prompt
from outwise.services.semantic_retrieval import allowed_in_jurisdiction


def section_path(item):
    return tuple((item.section or item.id).split(' / '))


def narrow_members(seed, parents):
    eligible = [p for p in parents if p.document_id == seed.document_id and allowed_in_jurisdiction(p, 'NO')]
    heading = section_path(seed)
    descendants = [p for p in eligible if len(section_path(p)) > len(heading)
                   and section_path(p)[:len(heading)] == heading]
    anchor = heading
    if not descendants and len(heading) > 1:
        ancestor = heading[:-1]
        branches = {section_path(p)[len(ancestor)] for p in eligible
                    if len(section_path(p)) > len(ancestor) and section_path(p)[:len(ancestor)] == ancestor}
        if len(ancestor) > 1 or len(branches) <= 1:
            anchor = ancestor
    branches = {section_path(p)[len(anchor)] for p in eligible
                if len(section_path(p)) > len(anchor) and section_path(p)[:len(anchor)] == anchor}
    exact_only = len(anchor) == 1 and len(branches) > 1
    members = [p for p in eligible if section_path(p) == anchor or not exact_only
               and len(section_path(p)) > len(anchor) and section_path(p)[:len(anchor)] == anchor]
    return (seed.document_id, anchor, exact_only), members


def pack_context(question, seeds, parents, count, budget=2000):
    results, seen, groups, texts = [], set(), set(), set()
    positions = {p.id: i for i, p in enumerate(parents)}
    for seed in seeds:
        if seed.item.id in seen:
            continue
        group, expanded = narrow_members(seed.item, parents)
        consecutive = max(positions[p.id] for p in expanded) - min(positions[p.id] for p in expanded) + 1 == len(expanded)
        same_heading = len({section_path(p) for p in expanded}) == 1
        if len(expanded) <= 3 and consecutive and (len(group[1]) > 1 or same_heading):
            members = expanded
        else:
            group, members = (seed.item.document_id, (seed.item.id,), True), [seed.item]
        if group in groups or ' '.join(seed.item.text.split()) in texts:
            continue
        groups.add(group)
        added = [RetrievedKnowledgeItem(p, seed.score) for p in members if p.id not in seen]
        # Keep the measured legacy budget envelope, independently of generation instructions.
        if count(_build_grounded_prompt(question, results + added)) > budget:
            continue
        results += added
        seen.update(p.item.id for p in added)
        texts.update(' '.join(p.item.text.split()) for p in added)
    return results
