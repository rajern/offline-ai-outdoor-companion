from __future__ import annotations

from outwise.knowledge.models import KnowledgeItem
from outwise.services.orchestrator import NO_GROUNDED_ANSWER, Orchestrator
from outwise.services.retrieval import RetrievalService


class RecordingModelService:
    def __init__(self, answer: str = "Grounded answer.") -> None:
        self.answer = answer
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.answer


def knowledge_item(
    item_id: str,
    text: str,
    *,
    title: str,
    source_name: str = "Stored source",
    source_url: str = "fixture://stored/source",
    topic: str = "test",
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        text=text,
        title=title,
        source_name=source_name,
        source_url=source_url,
        license="CC0-1.0",
        language="en",
        topic=topic,
    )


def test_model_receives_only_relevant_retrieved_context() -> None:
    relevant = knowledge_item(
        "ankle",
        "Rest the injured ankle and avoid further strain.",
        title="Ankle guidance",
        topic="ankle injury",
    )
    irrelevant = knowledge_item(
        "water",
        "Boil drinking water before use.",
        title="Water guidance",
        source_url="fixture://stored/water",
        topic="water hygiene",
    )
    model = RecordingModelService()
    orchestrator = Orchestrator(RetrievalService([relevant, irrelevant]), model)

    result = orchestrator.answer("How should I protect an injured ankle?")

    assert result.answer == "Grounded answer."
    assert len(model.prompts) == 1
    assert "Rest the injured ankle" in model.prompts[0]
    assert "Boil drinking water" not in model.prompts[0]
    assert "How should I protect an injured ankle?" in model.prompts[0]


def test_sources_come_from_metadata_and_are_deduplicated_in_rank_order() -> None:
    first = knowledge_item(
        "lost-a",
        "When lost, stop and assess your location.",
        title="Lost guidance A",
        source_name="Fixture manual",
        source_url="fixture://manual/lost",
        topic="lost navigation",
    )
    second = knowledge_item(
        "lost-b",
        "A lost hiker should remain visible when safe.",
        title="Lost guidance B",
        source_name="Fixture manual",
        source_url="fixture://manual/lost",
        topic="lost navigation",
    )
    model = RecordingModelService("See https://invented.example for details.")

    result = Orchestrator(RetrievalService([first, second]), model).answer(
        "I am a lost hiker."
    )

    assert result.answer == "See https://invented.example for details."
    assert [(source.source_name, source.source_url) for source in result.sources] == [
        ("Fixture manual", "fixture://manual/lost")
    ]
    assert result.sources[0].title in {"Lost guidance A", "Lost guidance B"}
    assert all("invented.example" not in source.source_url for source in result.sources)


def test_no_match_returns_honest_answer_without_calling_model() -> None:
    model = RecordingModelService()
    retriever = RetrievalService(
        [
            knowledge_item(
                "water",
                "Treat drinking water.",
                title="Water guidance",
                topic="water",
            )
        ]
    )

    result = Orchestrator(retriever, model).answer("quantum processor warranty")

    assert result.answer == NO_GROUNDED_ANSWER
    assert result.sources == ()
    assert model.prompts == []
