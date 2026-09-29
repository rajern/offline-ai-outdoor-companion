# Development knowledge fixtures

`development-knowledge.json` is a deliberately small synthetic dataset for
developing and testing Outwise retrieval. The text was written for this project;
it is not copied from an external manual or intended as production safety advice.
The fixture content is released under CC0-1.0.

`retrieval-evals.json` records representative questions, the fixture item IDs a
retriever should find, and the exact stored source identities expected in its
result. It is an initial regression set, not a claim that those are the only
relevant items for each question.

Both files use `schema_version: 1` and are loaded by
`outwise.knowledge.loader`. Real sources must pass the separate approval step in
M2-04 before they replace these fixtures.
