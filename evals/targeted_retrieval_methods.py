"""Experimental, source-preserving MiniLM views and packing. No eval/gold access."""
from __future__ import annotations

import json
import numpy as np

import run_retrieval_optimization_v1 as d
from optimization_embeddings import normalize


def text_windows(text, tokenizer, width):
    """Use token offsets, retaining every original character exactly once."""
    encoding = tokenizer.encode(text, add_special_tokens=False)
    if not encoding.ids:
        return [(text, 1)]
    boundaries = [0]
    for offset in range(width, len(encoding.ids), width):
        boundary = encoding.offsets[offset][0]
        if boundary > boundaries[-1]:
            boundaries.append(boundary)
    boundaries.append(len(text))
    return [(text[a:b], len(tokenizer.encode(text[a:b], add_special_tokens=False).ids) or 1)
            for a, b in zip(boundaries, boundaries[1:])]


def embedding_views(items, tokenizer, width=96, header_tokens=24):
    inputs, groups = [], []
    for item in items:
        header = f'{item["title"]}. {item.get("section") or ""}. '
        encoding = tokenizer.encode(header, add_special_tokens=False)
        if len(encoding.ids) > header_tokens:
            header = header[:encoding.offsets[header_tokens][0]].rstrip() + '. '
        windows = text_windows(item['text'], tokenizer, width)
        if ''.join(t for t, _ in windows) != item['text']:
            raise ValueError('Window offsets lost source characters')
        for contextual in [True, False]:
            indices, weights = [], []
            for body, weight in windows:
                value = header + body if contextual else body
                if len(tokenizer.encode(value).ids) > 128:
                    raise ValueError('Generated embedding view would be truncated')
                indices.append(len(inputs)); weights.append(weight); inputs.append(value)
            groups.append({'parent_id': item['id'], 'contextual': contextual,
                           'indices': indices, 'weights': weights})
    return inputs, groups


def parent_vectors(vectors, groups):
    views = []
    for group in groups:
        value = np.average(vectors[group['indices']], axis=0, weights=group['weights'])
        views.append(value)
    views = normalize(np.asarray(views, dtype=np.float32))
    return normalize((views[0::2] + views[1::2]) / 2)


def scope_key(item):
    return (item.document_id, item.title, item.section, json.dumps(item.metadata, sort_keys=True),
            ' '.join(item.text.split()))


def instruction_unit(seed, parents, jurisdiction):
    """Keep the nearest preceding ancestor and same-heading contiguous text.

    Source hierarchy is the only dependency signal. This preserves explicit
    parent scope without guessing medical dependencies from keywords. Dependencies
    across unrelated headings cannot be guaranteed and remain a measured limit.
    """
    eligible = [p for p in parents if p.document_id == seed.document_id
                and d.allowed_in_jurisdiction(p, jurisdiction)]
    position = next(i for i, p in enumerate(eligible) if p.id == seed.id)
    heading = d.section_path(seed)
    start, end = position, position + 1
    while start > 0 and d.section_path(eligible[start - 1]) == heading:
        start -= 1
    while end < len(eligible) and d.section_path(eligible[end]) == heading:
        end += 1
    ancestors = [(i, p) for i, p in enumerate(eligible[:start])
                 if len(d.section_path(p)) < len(heading)
                 and heading[:len(d.section_path(p))] == d.section_path(p)]
    prefix = []
    if ancestors:
        _, ancestor = max(ancestors, key=lambda pair: (len(d.section_path(pair[1])), pair[0]))
        ancestor_heading = d.section_path(ancestor)
        a = next(i for i, p in enumerate(eligible) if p.id == ancestor.id)
        while a > 0 and d.section_path(eligible[a - 1]) == ancestor_heading:
            a -= 1
        prefix = eligible[a:next(i for i, p in enumerate(eligible) if p.id == ancestor.id) + 1]
    return prefix + eligible[start:end]


def diverse_pack(case, seeds, parents, counter, budget=2000):
    first, rest, docs = [], [], set()
    for rank, seed in enumerate(seeds, 1):
        if seed.item.document_id not in docs:
            first.append((rank, seed)); docs.add(seed.item.document_id)
        else:
            rest.append((rank, seed))
    results, packets, trace, seen, scopes = [], [], [], set(), set()
    for rank, seed in first + rest:
        if seed.item.id in seen:
            continue
        members = instruction_unit(seed.item, parents, case['jurisdiction'])
        added = [d.RetrievedKnowledgeItem(p, seed.score) for p in members
                 if p.id not in seen and scope_key(p) not in scopes]
        if not added:
            continue
        tokens, key = counter.count(d._build_grounded_prompt(case['question'], results + added))
        entry = {'seed_rank': rank, 'seed_id': seed.item.id, 'score': seed.score,
                 'would_add': [p.item.id for p in added], 'prompt_tokens': tokens,
                 'tokenization_key': key}
        if tokens > budget:
            trace.append({**entry, 'status': 'over_budget'})
            continue
        results += added; seen.update(p.item.id for p in added)
        scopes.update(scope_key(p.item) for p in added)
        trace.append({**entry, 'status': 'accepted'}); packets.append(entry)
    return results, packets, trace
