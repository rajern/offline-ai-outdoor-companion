from pathlib import Path
from urllib.request import Request

import pytest

from outwise.knowledge.ingestion import (
    ExactURLRedirect, IngestionError, SnapshotStore, chunk_section,
    digest, extract_article, geography, write_json,
)


def test_article_preserves_owner_sections_and_omits_navigation_and_media():
    raw = ("<nav>UNRELATED</nav><main><h1>Test article</h1>"
           "<h2>Adults</h2><h3>First step</h3><p>" + "Synthetic instruction. " * 15 + "</p>"
           "<figure><p>IMAGE CAPTION</p></figure>"
           "<!-- navigation -->"
           "<p>Innhaldet er levert og kvalitetssikra av Test owner Slik refererer du til innhaldet</p>"
           "<p>Sist oppdatert 6. oktober 2026</p></main>").encode()
    title, sections, metadata = extract_article(raw, "helsenorge")
    assert title == "Test article"
    assert sections[0][0] == "Adults / First step"
    assert metadata == {"content_owner": "Test owner", "source_updated_at": "2026-10-06", "source_language": None}
    text = " ".join(t for _, t in sections)
    assert "UNRELATED" not in text and "IMAGE CAPTION" not in text
    assert "Test owner" not in text
    assert "navigation" not in text


def test_snapshot_rebuild_is_offline_and_detects_tampering(tmp_path: Path):
    raw = b"<html>Frozen source</html>"
    sha = digest(raw)
    path = tmp_path / "raw" / (sha + ".html")
    path.parent.mkdir()
    path.write_bytes(raw)
    write_json(tmp_path / "snapshots.json", {"https://example.test/article": {"raw_snapshot_sha256": sha}})
    store = SnapshotStore(tmp_path)
    assert store.get("https://example.test/article")[0] == raw
    with pytest.raises(IngestionError, match="No frozen snapshot"):
        store.get("https://example.test/other")
    path.write_bytes(b"Changed")
    with pytest.raises(IngestionError, match="Corrupt"):
        store.get("https://example.test/article")


def test_redirect_cannot_expand_approved_allowlist():
    handler = ExactURLRedirect()
    with pytest.raises(IngestionError, match="Unapproved redirect"):
        handler.redirect_request(Request("https://example.test/a"), None, 302, "", {}, "https://example.test/b")


def test_geography_marks_local_operational_details():
    assert geography("doc", "If lost", "Call 111 for help", "NZ")["jurisdiction"] == "NZ"
    assert geography("doc", "If lost", "Stay put and keep warm", "NZ")["jurisdiction"] == "general"
    assert geography("doc", "Registration", "Register your beacon", "NZ")["is_location_specific"]
    assert geography("nws", "Help", "Call 911", "US")["jurisdiction"] == "US"


def test_chunking_preserves_all_words_in_long_paragraph():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_section(text, max_chars=200)
    assert " ".join(chunks).split() == text.split()
    assert max(map(len, chunks)) <= 200
