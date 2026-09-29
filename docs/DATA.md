# Outwise — Data

## Goal

Outwise should use a small, curated and legally reusable knowledge base rather than collecting large amounts of uncontrolled web content.

The data system should make it easy to add or replace sources without changing retrieval or application logic.

## Data principles

- Prefer complete datasets, APIs, manuals or document collections over scraping individual web pages.
- Avoid manual copy/paste workflows.
- Every source must have a clear provenance and licence status before it is included in the real knowledge base.
- Safety-critical information should come from trustworthy sources.
- English and Norwegian source material can both be used.
- The model may answer in the user's language even when retrieved source material is in another language.
- Raw source data should remain separate from normalized Outwise data.

## Knowledge areas

The initial knowledge base should focus on:

- injuries and basic first aid
- cold exposure and hypothermia
- getting lost and basic navigation
- shelter, warmth and fire
- water and hygiene
- weather and natural hazards
- emergency signalling and prioritization
- basic outdoor survival and preparedness

High-risk areas such as plant, mushroom and animal identification are outside the MVP.

## Common data contract

All knowledge used by retrieval should be normalized into a common structure.

Each knowledge item should contain at least:

- `id`
- `text`
- `title`
- `source_name`
- `source_url`
- `license`
- `language`
- `topic`

Optional metadata may include:

- `section`
- `published_at`
- `updated_at`
- `document_id`
- additional source-specific metadata

The executable version 1 contract lives in `backend/outwise/knowledge/models.py`.
Normalized JSON files use a top-level `schema_version` and `items` list.
Source-specific values belong in the optional `metadata` object rather than in
new top-level fields, so retrieval can remain source-independent. Development
examples and their retrieval regression set live in `knowledge/fixtures/`.

Retrieval should only depend on this normalized format, not on the original source format.

## Ingestion

Each approved source may have its own ingestion adapter.

The general flow is:

    Source
      ↓
    Parse
      ↓
    Normalize
      ↓
    Chunk
      ↓
    Validate
      ↓
    Generate embeddings
      ↓
    Local knowledge store

The ingestion process should be automated wherever practical.

Supported source formats may include:

- JSON
- structured APIs
- PDF/manual collections
- other structured downloadable formats

Web scraping should only be introduced if a strong source cannot reasonably be obtained another way.

## Source approval

Before a real source is included, verify:

1. The source is relevant to the Outwise use cases.
2. The information is trustworthy enough for its intended use.
3. The licence or terms allow the intended reuse and distribution.
4. Required attribution can be preserved.
5. The source can be ingested without unreasonable manual work.

Approved production sources should be recorded in this file or an associated manifest.

## Development data

RAG development should begin with a very small fixture dataset.

The fixture data exists only to:
- implement ingestion
- test retrieval
- test source metadata
- test end-to-end RAG behaviour

It should not be treated as the final knowledge base.

## Storage and retrieval

The knowledge base must work fully offline.

The expected approach is:
- normalized chunks stored locally
- source metadata stored with each chunk
- pre-generated embeddings stored locally
- local semantic retrieval
- optional full-text search if useful

A dedicated vector database is not required for the MVP unless the final dataset becomes large enough to justify one.

The exact local storage implementation may be chosen during development as long as it remains simple, local and replaceable.

## Source handling in responses

Retrieved knowledge must preserve its source identity.

The model may combine multiple retrieved chunks into a natural answer, but the application should display the real sources used to support that answer.

Source names and URLs should come from stored metadata rather than being invented by the language model.

## Repository rules

Do not commit:
- large generated knowledge databases
- model files
- embeddings unless intentionally small test fixtures
- source material whose licence does not allow redistribution

The public repository may contain:
- ingestion code
- schemas
- source manifests
- small synthetic/test fixtures
- documentation describing how to obtain approved source data

## Real knowledge base milestone

The final source selection is intentionally deferred until the RAG system works with fixtures.

During the real knowledge-base milestone:

1. Identify candidate datasets and document collections.
2. Verify licences and attribution requirements.
3. Select the smallest set that covers the MVP knowledge areas well.
4. Build automated ingestion adapters.
5. Normalize and validate the data.
6. Generate the local retrieval assets.
7. Review the resulting knowledge base before it is used by the MVP.
