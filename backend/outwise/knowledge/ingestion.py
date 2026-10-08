"""Allowlisted HTML ingestion; frozen, hash-checked snapshots precede extraction."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from outwise.knowledge.loader import load_knowledge_items


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "knowledge/manifests/approved-sources.json"
DEFAULT_LOCAL = ROOT / "knowledge/local"
EXTRACTOR_VERSION = "html-sections-v3"
SELECTORS = {
    "helsenorge": "main",
    "doc": "#main-content, main, article, .main-content",
    "varsom": "article, main, #main-content",
    "cdc": "main, #content",
    "nws": ".cms-content",
}


class IngestionError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("approval", {}).get("status") != "approved":
        raise IngestionError("Source manifest requires explicit owner approval")
    sources = manifest["sources"]
    for field in ("id", "url"):
        if len({s[field] for s in sources}) != len(sources):
            raise IngestionError(f"Duplicate source {field}")
    for source in sources:
        publisher = manifest["publishers"][source["publisher"]]
        for url in (source["url"], publisher["licence_url"]):
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username:
                raise IngestionError(f"Invalid HTTPS source: {url}")
    return manifest


class ExactURLRedirect(HTTPRedirectHandler):
    """Allow only a trailing slash canonicalization, never another article."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if newurl.rstrip("/") != req.full_url.rstrip("/"):
            raise IngestionError(f"Unapproved redirect: {req.full_url} -> {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class SnapshotStore:
    def __init__(self, directory: Path, *, offline: bool = True):
        self.directory = directory
        self.offline = offline
        self.registry_path = directory / "snapshots.json"
        self.registry = json.loads(self.registry_path.read_text(encoding="utf-8")) if self.registry_path.exists() else {}

    def get(self, url: str) -> tuple[bytes, dict]:
        if url in self.registry:
            record = self.registry[url]
            sha = record["raw_snapshot_sha256"]
            if not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise IngestionError("Invalid snapshot hash")
            raw = (self.directory / "raw" / (sha + ".html")).read_bytes()
            if digest(raw) != sha:
                raise IngestionError(f"Corrupt snapshot for {url}")
            return raw, record
        if self.offline:
            raise IngestionError(f"No frozen snapshot for {url}; run ingestion with --fetch")
        request = Request(url, headers={"User-Agent": "Outwise-MVP/0.1 (curated offline knowledge build)", "Accept": "text/html"})
        with build_opener(ExactURLRedirect()).open(request, timeout=35) as response:
            if "text/html" not in response.headers.get("Content-Type", ""):
                raise IngestionError(f"Expected HTML at {url}")
            raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise IngestionError(f"Source too large: {url}")
            record = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "resolved_url": response.url,
                      "raw_snapshot_sha256": digest(raw)}
        raw_path = self.directory / "raw" / (record["raw_snapshot_sha256"] + ".html")
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw)
        self.registry[url] = record
        write_json(self.registry_path, self.registry)
        return raw, record


def _clean(text: str) -> str:
    return " ".join(text.split())


def extract_article(raw: bytes, publisher: str) -> tuple[str, list[tuple[str, str]], dict]:
    soup = BeautifulSoup(raw, "html.parser")
    root = soup.select_one(SELECTORS[publisher])
    if root is None:
        raise IngestionError(f"No article container for {publisher}; extractor needs review")
    title_node = root.find("h1") or soup.find("h1")
    if title_node is None:
        raise IngestionError("Missing article title")
    title = _clean(title_node.get_text(" "))
    document_language = soup.html.get("lang", "") if soup.html else ""
    if publisher == "doc":
        og_title = soup.find("meta", property="og:title")
        if not og_title or not og_title.get("content"):
            raise IngestionError("DOC article title metadata missing")
        title = _clean(og_title["content"])
    full_text = _clean(root.get_text(" "))
    owner = None
    if publisher == "helsenorge":
        owner_match = re.search(r"(?:Innholdet|Innhaldet) er levert(?: og kvalitetssikr(?:et|a))? av\s+(.+?)(?:Slik refererer|Sist oppdatert|Sist faglig|Kontakt|$)", full_text)
        owner = owner_match.group(1).strip() if owner_match else None
        if not owner:
            raise IngestionError(f"Missing article content owner: {title}")
    updated = None
    date_match = re.search(r"(?:Sist oppdatert|Last updated|Sist faglig oppdatert)[: ]+(\d{1,2})[.](\d{1,2})[.](\d{4})", full_text)
    if date_match:
        d, m, y = date_match.groups()
        updated = f"{y}-{int(m):02}-{int(d):02}"
    else:
        months = ['januar','februar','mars','april','mai','juni','juli','august','september','oktober','november','desember']
        match = re.search(r"Sist oppdatert\s+(\d{1,2})\.\s+(\w+)\s+(\d{4})", full_text)
        if match and match[2].casefold() in months:
            updated = f"{match[3]}-{months.index(match[2].casefold()) + 1:02}-{int(match[1]):02}"
    for node in root.select("script, style, nav, footer, aside, form, iframe, video, audio, img, figure, svg, button, .feedback, .article-feedback"):
        node.decompose()
    sections: list[tuple[str, str]] = []
    heading = title
    headings: dict[int, str] = {}
    paragraphs: list[str] = []
    stopped = False

    def walk(node):
        nonlocal heading, headings, paragraphs, stopped
        if stopped or isinstance(node, Comment):
            return
        if isinstance(node, Tag) and node.name in {"h2", "h3", "h4"}:
            text = _clean(node.get_text(" "))
            if not text:
                return
            # Callout headings are part of the warning, not parents of later sections.
            if publisher == "cdc" and node.find_parent(class_=re.compile("callout|alert|notice")):
                paragraphs.append(text)
                return
            if paragraphs:
                sections.append((heading, "\n".join(paragraphs)))
            level = int(node.name[1])
            headings = {k: v for k, v in headings.items() if k < level}
            headings[level] = text
            heading, paragraphs = " / ".join(headings.values()), []
            return
        if isinstance(node, Tag) and node.name == "h1":
            return
        if isinstance(node, NavigableString) or (isinstance(node, Tag) and node.name in {"p", "li", "td"} and not node.find(["p", "li", "td", "h2", "h3", "h4"])):
            text = _clean(str(node) if isinstance(node, NavigableString) else node.get_text(" "))
            if re.match(r"(?:Innholdet|Innhaldet) er levert|Slik refererer du|Sist oppdatert", text):
                stopped = True
                return
            if text and text not in paragraphs:
                paragraphs.append(text)
            return
        if isinstance(node, Tag):
            for child in node.children:
                walk(child)

    walk(root)
    if paragraphs:
        sections.append((heading, "\n".join(paragraphs)))
    if sum(len(t) for _, t in sections) < 200:
        raise IngestionError(f"Empty/short extracted article: {title}")
    return title, sections, {"content_owner": owner, "source_updated_at": updated,
                             "source_language": document_language.split("-")[0] or None}


_LOCATION_PATTERNS = {
    "doc": r"\b(New Zealand|NZ|111|Department of Conservation|DOC|Aotearoa|Fire and Emergency|public conservation land|Check it'?s alright|NZSAR|Maritime|Rescue Coordination|national parks?|permits?|legal|bylaw|registration)\b|doc\.govt|beacons\.org|checkitsalright|fireandemergency|adventuresmart",
    "cdc": r"\b(911|United States|U\.S\.|FDA|EPA)\b",
    "nws": r"\b(911|United States|U\.S\.|National Weather Service|NOAA)\b",
}


def geography(publisher: str, section: str, text: str, default: str) -> dict:
    location_specific = publisher in {"helsenorge", "varsom"}
    if publisher in _LOCATION_PATTERNS:
        location_specific = bool(re.search(_LOCATION_PATTERNS[publisher], section + " " + text, re.I))
    return {"jurisdiction": default if location_specific else "general",
            "geographic_scope": default if location_specific else "general",
            "is_location_specific": location_specific,
            "validity_type": "jurisdiction_specific" if location_specific else "evergreen"}


def chunk_section(text: str, max_chars: int = 1100) -> list[str]:
    """Keep paragraphs intact where possible; never silently drop a long paragraph."""
    parts = []
    current = ""
    for paragraph in text.splitlines():
        while len(paragraph) > max_chars:
            split_at = paragraph.rfind(" ", 0, max_chars)
            split_at = split_at if split_at > 0 else max_chars
            if current:
                parts.append(current)
                current = ""
            parts.append(paragraph[:split_at])
            paragraph = paragraph[split_at:].strip()
        if len(current) + len(paragraph) + 1 > max_chars and current:
            parts.append(current)
            current = ""
        current = "\n".join(filter(None, (current, paragraph)))
    if current:
        parts.append(current)
    return parts


def build_knowledge(manifest_path: Path, local: Path, *, fetch: bool = False) -> Path:
    manifest = load_manifest(manifest_path)
    store = SnapshotStore(local, offline=not fetch)
    rights = {}
    for key, publisher in manifest["publishers"].items():
        raw, record = store.get(publisher["licence_url"])
        text = _clean(BeautifulSoup(raw, "html.parser").get_text(" ")).casefold()
        if not all(marker.casefold() in text for marker in publisher["rights_markers"]):
            raise IngestionError(f"Reuse terms need review: {key}")
        rights[key] = record
        print(f"Verified terms: {key}", flush=True)
    items = []
    for source in manifest["sources"]:
        publisher = manifest["publishers"][source["publisher"]]
        raw, record = store.get(source["url"])
        title, sections, extracted = extract_article(raw, source["publisher"])
        content_sha = digest("\n".join(t for _, t in sections).encode("utf-8"))
        count = 0
        for section, text in sections:
            # Footer metadata and sharing/navigation must not enter the RAG context.
            if re.search(r"^(Innholdet er levert|Innhaldet er levert|Sist oppdatert|Referanser|References|Related|Resources|Mer informasjon|Kontakt|Share|Feedback)", section, re.I):
                continue
            if source["publisher"] == "varsom" and re.match(r"Isvettregl.*(?:flyte|Livredningsselskap)", section, re.I):
                continue  # Third-party credited rules are outside the publisher's reuse grant.
            geo = geography(source["publisher"], section, text, publisher["jurisdiction"])
            for chunk in chunk_section(text):
                count += 1
                metadata = {**record, **extracted, **geo, "coverage": source["coverage"],
                            "licence_url": publisher["licence_url"],
                            "attribution_requirements": publisher["attribution_requirements"],
                            "licence_checked_at": rights[source["publisher"]]["retrieved_at"],
                            "licence_snapshot_sha256": rights[source["publisher"]]["raw_snapshot_sha256"],
                            "content_sha256": content_sha, "extractor_version": EXTRACTOR_VERSION,
                            "changes": "Article text extracted, normalized and split into sections/chunks; media omitted."}
                metadata["content_owner"] = extracted["content_owner"] or publisher["name"]
                if source["publisher"] == "helsenorge":
                    metadata["copy_notice"] = f"Denne artikkelen vart kopiert frå {source['url']} {record['retrieved_at'][:10]}. Teksten kan ha vorte oppdatert på helsenorge.no."
                items.append({"id": f"{source['id']}-{count:03}", "document_id": source["id"],
                              "text": chunk, "title": title, "section": section,
                              "source_name": publisher["name"], "source_url": source["url"],
                              "license": publisher["license"], "language": extracted["source_language"] or publisher["language"],
                              "topic": section, "updated_at": extracted["source_updated_at"], "metadata": metadata})
        if not count:
            raise IngestionError(f"No retained chunks for {source['id']}")
        print(f"Extracted {source['id']}: {count} chunks", flush=True)
    # Validate before publishing a new normalized build.
    candidate = local / "knowledge.candidate.json"
    write_json(candidate, {"schema_version": 1, "items": items})
    load_knowledge_items(candidate)
    output = local / "knowledge.json"
    candidate.replace(output)
    write_json(local / "build.json", {"manifest_sha256": digest(manifest_path.read_bytes()),
               "knowledge_sha256": digest(output.read_bytes()), "extractor_version": EXTRACTOR_VERSION,
               "documents": len(manifest["sources"]), "chunks": len(items),
               "snapshots": store.registry})
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--local", type=Path, default=DEFAULT_LOCAL)
    parser.add_argument("--fetch", action="store_true", help="Fetch missing allowlisted snapshots (existing snapshots stay frozen)")
    args = parser.parse_args()
    print(build_knowledge(args.manifest, args.local, fetch=args.fetch))


if __name__ == "__main__":
    main()
