# Approved offline knowledge

The project owner approved the 22 URLs in `knowledge/manifests/approved-sources.json`
on 2026-10-06 in this chat, together with Norway as the MVP jurisdiction and
Norwegian answers. This approval covers the source set and implementation of
M2-05/06; it does not approve M3 safety policy, final legal product copy or release.

## Setup on Windows

First install backend dependencies using `backend/README.md` and prepare Qwen
using `docs/MODEL_SETUP.md`. From the repository root:

```powershell
.\scripts\setup-knowledge.ps1
```

Setup fetches exactly the manifest's article URLs and five reuse-policy URLs.
It does not follow article links, crawl sites, or substitute another source.
Only a trailing slash redirect is accepted. Source-specific HTML extraction,
normalization and section chunking happen outside retrieval.

Generated assets are in `knowledge/local/`, which is ignored by Git:

- `raw/<sha256>.html`: frozen HTML snapshots, including reuse terms
- `snapshots.json`: retrieval dates, resolved URLs and raw hashes
- `knowledge.json`: normalized version-1 chunks and full provenance metadata
- `build.json`: manifest/knowledge hashes and extractor version
- `embedding-model/`: pinned, quantized multilingual embedding model and file hashes
- `embeddings.npy`, `index.json`: local vectors, chunk order and integrity checks
- `retrieval-report.json`: local evaluation details
- `answer-report.json`: generated answers for manual review, when requested

Existing snapshots are never silently refreshed. To create a fresh snapshot set,
run the ingestion module with `--local` pointing to a new directory, then run
the embeddings and evaluation modules with the same `--local`. Keep the old
directory to reproduce the previous knowledge build. No raw or generated KB
assets are published by these commands.

Rebuild from frozen data without network access:

```powershell
.\scripts\setup-knowledge.ps1 -Offline
```

The knowledge JSON is deterministic for a frozen snapshot set and extractor
version. The embedding model revision and its file hashes are pinned; index
metadata also records the FastEmbed version. Floating-point embeddings may
differ slightly across CPU/runtime versions. Runtime verifies knowledge/index
hashes and model identity instead of silently using stale vectors.

## Retrieval and scope

The real KB uses local multilingual MiniLM embeddings and cosine ranking. No vector
database or cloud service is needed. Norwegian and English content can match
queries in either language. A similarity threshold supports abstention but is
not a safety guarantee. The checked-in evaluation questions are regression
checks, not a comprehensive quality assessment.

Norway is the default jurisdiction. NO-specific and general chunks are usable;
NZ/US-specific operational content and `dynamic_do_not_cache` chunks are
excluded before context selection. Publisher-specific classification is
conservative and must be reviewed when sources change. Real-time warnings,
forecasts, source images/video and third-party credited rule collections are
excluded from normalized knowledge. Frozen raw HTML is retained only locally.

Knowledge coverage follows the owner's narrowed shelter scope: exposure
protection, warmth, equipment and fire safety. Detailed bushcraft is outside
scope. Frostbite-specific and dedicated cold-water shock guidance remain gaps.
NZ fire regulation sections are retained with provenance but cannot be used for
Norwegian answers, which limits generic fire coverage.

## Source reuse

Helsenorge text reuse must preserve article content owner, original URL and
retrieval date. Whole-article copies must carry a dated copy/possible-update
notice, retained in each item's metadata. DOC material is CC BY 4.0 except
third-party material, logos and design elements. Varsom requires credit and
direct-link attribution for quotations. CDC and NWS reuse is subject to the
manifest's attribution and non-endorsement requirements, with third-party
material excluded. Terms are frozen during setup and checked for known reuse
markers; unrecognized statements stop the build. Marker checks are not legal
analysis and cannot detect every changed condition. Fresh snapshots require
renewed owner review if the reuse terms have changed.

CDC material is developed by CDC and available free on its website. Its use
does not imply endorsement by CDC, ATSDR, HHS or the United States Government.
Outwise's generated summaries are not official CDC or NWS material. These are
source reuse notices; final product safety/legal messaging remains an M3-02
owner checkpoint.

## Owner quality review after M2-06

### Validation status (2026-10-06)

M2-05 is complete; M2-06 is not complete. The application uses real local
knowledge, source attribution is displayed, and frozen ingestion/index builds
and retrieval were exercised with Python network connections forbidden.
68 backend tests, frontend typechecking and the web export pass. The 13
retrieval cases pass their document-level hit-at-3 checks, including an
unsupported question that produces no context. These checks do not verify
that the right instruction chunk was selected or that generated advice is true.

Manual answer checks found substantial issues:

- The ankle case finds the approved injury article but retrieves fracture
  instructions instead of the article's sprain treatment section. Generated
  advice mixes these situations.
- Water queries retrieve CDC overview text alongside unrelated heat advice.
  Some generated answers invent treatment details absent from their context.
- The avalanche case retrieves an overview plus unrelated cold/rescue context.
  The approved overview links to more detailed guidance outside the allowlist;
  those pages have deliberately not been fetched. Generated answers add
  unsupported details rather than reliably admitting this gap.
- Several Norwegian responses contain broken wording or meaning.

A shorter grounding prompt and lower sampling temperature were tested, as
were greedy generation and explicit CPU execution. They did not resolve all
issues. No model, runtime version or approved source decision was changed.
One English-language water control stayed within the same retrieved context,
but this single result does not validate English output generally. The exact
contribution of retrieval versus model limitations remains unresolved.
Repair retrieval/grounding and repeat factual answer review before closing
M2-06. A different generation model or an expanded source allowlist requires
owner approval first. Do not use this build for real-world emergency guidance.

To generate a local answer report for inspection (not an automatic quality pass):

```powershell
cd backend
.\.venv\Scripts\python.exe -m outwise.knowledge.evaluate --answers --offline-check
```

Run the app and try `evals/real-knowledge.json` plus paraphrases and combined
scenarios. Review retrieval relevance, Norwegian answer quality, source
correctness and missing knowledge. Automated checks do not approve product
quality. M3 must wait for explicit owner approval.
