# M2-06: nytt eksplisitt preflight-forsøk, 2026-10-24

Eier ba «prøv igjen». Omtrent 4 141,93 MiB verts-RAM var tilgjengelig ved
innledende kontroll. Den gamle 2B-forseglingen og modellmanifestet for 4B ble
verifisert og gjenbrukt i en separat arbeidsmappe. Ingen modell ble lastet ned
på nytt, og ingen gamle svar ble kjørt igjen.

4B-lastingen stoppet på samme uendrede reservekrav:

- Minimum tilgjengelig verts-RAM: **158,79 MiB**, krav minst 256 MiB.
- Høyeste målt prosessgruppe-RSS: **749,08 MiB**, grense 4 096 MiB.
- Lastingen ble avbrutt tidligere enn i forrige forsøk. RSS-tallet er derfor
  ikke modellens ferdiglastede minnebehov eller et bevis på redusert RAM-behov.
- Nye genererte svar, dommerkall og betalte API-kall: **0**.
- Egen server er avsluttet; etterkontroll fant ingen gjenværende llama-server.

Rådata bevares under
`knowledge/local/diagnostics/local-generation-comparison-retry-2026-10-24/`.
`resume-lineage.json` binder forrige stopp, opprinnelig input-freeze og den
gjenbrukte 2B-forseglingen. Alle tidligere forsøk og kontrollresultater er uendret.
JSON-auditen ved siden av denne rapporten binder nye logger med hashes.

2B er fortsatt klar på de 36 planlagte inputene. 4B- og Gemma-preflight samt
hele svarkvalitetssammenligningen er uferdig. For videre kjøring må mer verts-RAM
frigjøres, eller eier eksplisitt avgrense modellutvalget. Grensene økes ikke,
modeller utelates ikke automatisk på grunn av dette vertsminnebruddet, og ingen
ny last startes automatisk. Holdout, produksjon og M3 er urørt.
