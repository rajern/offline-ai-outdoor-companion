# Qwen3-Embedding Q4 — avgrenset stabilitetsdiagnostikk

2026-10-08. **Anbefaling A: CPU-rettelsen løser den målte variasjonen, og
Qwen Q4 består den opprinnelige reproducerbarhetskontrollen.** Ingen toleranse
er senket. Qwen kan beholdes i fase A-planen. Fase A/B/C er ikke startet;
resten av forsøksflyten og ressurskontrollene er fortsatt uferdige.

## Årsak og rettelse

Eval-adapteren bruker nå eksplisitt `--device none --no-op-offload
--no-kv-offload`. Modell, pooling, fire tråder, batchgrenser, float32 KV,
Flash Attention av og eksisterende cachevern er beholdt. Produksjonskode er
uendret. Modellhash er fortsatt
`470901844f8cb73a3e0479ea1dd57ad1baba7072481f1897b2dc4b132b9051a7`;
llama.cpp er fortsatt b11193 / `4e7481175`.

**Bekreftet:** Den samlede CPU-isolasjonen gir identiske embeddings i de
gjennomførte kontrollene. Det gamle oppsettet satte bare GPU-lag til null.
Den installerte versjonen har separate innstillinger for enheter, operation
offload og KV-offload; de to sistnevnte er normalt aktivert.
Se [versjonens serverdokumentasjon](https://github.com/ggml-org/llama.cpp/blob/4e7481175/tools/server/README.md)
og [backendinitialisering og standardinnstillinger](https://github.com/ggml-org/llama.cpp/blob/4e7481175/src/llama-context.cpp).

**Mest sannsynlig forklaring:** Den tidligere tillatte accelerator-/offload-banen
ga variasjonen. Tidligere logger viser Vulkan-minneallokering til tross for
null GPU-lag; disse advarslene finnes ikke i de nye loggene. Hvilket av de tre
flaggene, hvilken kjerne eller hvilken maskinvare som forklarer effekten alene,
er **ikke isolert**. Vi har ikke påvist en Q4-modellfeil eller bevist en spesifikk
llama.cpp-bug. Ytterligere årsaksforskning er ikke nødvendig for denne rettelsen.

## Fast testomfang og resultater

Planen ble lagret før embeddings: fire spørsmål og 24 syntetiske passasjer om
kulde/vind, matlaging, vann og torden, med nærliggende formuleringer. Ingen gold
eller kildefasit brukes. To komplette målinger i hver av to uavhengige prosesser
gir seks parvise sammenligninger, hvorav fire mellom prosesser. Fire spørsmål
gir 24 spørsmål/par og 96 top-k-medlemskapskontroller.

| Måling etter rettelsen | Resultat |
|---|---:|
| Største forskjell per normalisert float32-komponent | 0 |
| Laveste repeat cosine | 1,0 |
| Største forskjell i kandidat-cosine | 0 |
| Endret full rangering | 0/24 |
| Endret medlemskap i top-k 3 / 5 / 8 / 16 | 0/24 for hver k |
| Kryssing av diagnostiske terskler | 0 for hver k |
| Ulike token-ID-er for samme input | 0 |

Scores er stabile både når dokumentvektorene regenereres og når dokumentindeksen
holdes fast. Tersklene er midtpunktet mellom referansens k-te og neste score,
definert før kjøring; dette undersøker lokale beslutningsgrenser og er **ikke**
kalibrering av fase B. Resultatfilen viser grenseavstander og passasjeindekser.
Tokenantallet fra `/tokenize` med special tokens stemmer med embeddingresponsens
rapporterte antall. Alle responser har 1024 dimensjoner; L2-norm før adapterens
normalisering er 0,99999994–1,0. Last-token pooling er uendret, slik
[Qwens GGUF-anvisning](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF) beskriver.

Den opprinnelige syntetiske inputsekvensen består i begge prosessene, og den
uendrede `preflight_retrieval_optimization.py` består separat i en tredje ny
prosess (`attempt-06`): dimensjoner, normalisering og
`np.allclose(query, repeated, atol=1e-5)`, med uendret standard `rtol=1e-5`.
Derfor kjøres ikke de betingede én-tråds-/F16-forsøkene.

Historiske feil er bevart: opp til 0,01406 komponentforskjell og 0,996871 cosine,
og 0,001127 / 0,999972 mellom to gamle prosesser. **Rangeringsvirkningen i det
urettede oppsettet ble ikke målt.** Vi hevder bare stabil rangering etter
rettelsen på dette korte, syntetiske settet, ikke på hele kildebasen eller
ved alle mulige grensetilfeller. Ingen retrieval-kvalitet eller vinner er vurdert.

## Ressurser, etterprøvbarhet og stoppunkt

Totalt 130 lokale embeddingforespørsler: 124 i diagnostikken og seks i original
preflight. Summert kjøretid 25,20 s; samplet CPU-tid omtrent 80,78 CPU-s.
Samtidig RSS for Python og server toppet rundt 2,69 GB, målt hver 100 ms.
Tilgjengelig maskin-RAM falt til 309 MB i hoveddiagnostikken og 51 MB i den
separate originalkontrollen. Ingen parallelle modellprosesser ble startet.
Dette etablerer ikke kapasitet for full corpuskjøring eller mobilbruk.

17 tekniske tester består: fem stabilitets-/adaptertester, fem packing-/stopptest
og syv scorer-/cachetester, alle uten modell- eller dommerkall. Første sandbox-
oppstart fikk ikke lokal health-forbindelse og stoppet før embeddings; loggen
er bevart separat. Den samme avgrensede kjøringen fungerte med lokal
prosesstilgang. Ingen nye modeller, bygg eller avhengigheter ble installert.

[Maskinlesbare resultater](qwen_embedding_stability_results.v1.json) inneholder
innstillinger, hashes, ressurser og artefaktmanifest. Råvektorer, tokens, server-
kommandoer og logger ligger under ignorert
`knowledge/local/diagnostics/qwen-stability-v1-2026-10-08-cpu/`;
original preflight under `retrieval-optimization-v1-2026-10-08/model-preflight/`.
Diagnostikkens eksakte kodesnapshot er bevart. Den brukte eksplisitte CPU-argumenter;
samme rettelse ble deretter gjort til standard og verifisert av originaltesten.
Implementasjonen er pushet som `c7d3c3b`.

**Enkleste videre løsning:** Behold Qwen Q4 med de tre CPU-flaggene og den
opprinnelige akseptkontrollen. Ingen kriterieendring eller tomodellsplan trengs.
Ved neste autoriserte optimaliseringsrunde må gjenværende orkestrering ferdigstilles
og tilstrekkelig minne bekreftes før full drift. Denne oppgaven stopper her:
0/31 konfigurasjoner, 0 dommerkall, 0 API-kall, ingen holdout-tilgang,
produksjonsendring, svargenerering, gold-endring eller overskrevne historiske logger.
