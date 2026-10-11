# M2-06: kontrollert genereringssammenligning — preflight-stopp

**Status 2026-10-11:** Sammenligningen er ikke gjennomført. Den opprinnelige
verts-RAM-kontrollen stoppet under lasting av eksisterende Qwen3.5-2B og MiniLM.
Ingen nye modellsvar ble generert, og det finnes ingen ny modellvinner.

| Måling | Observert | Opprinnelig grense |
|---|---:|---:|
| Laveste tilgjengelige verts-RAM | 140,72 MiB | minst 256 MiB |
| Høyeste samlet prosessgruppe-RSS | 748,72 MiB | høyst 4 096 MiB |
| CPU brukt i preflight | 5,47 CPU-sekunder | rapporteres separat |
| Nye genererte svar / dommerkall / betalte API-kall | 0 / 0 / 0 | ingen betalte API |

Ressursutvalget varte 5,24 sekunder og ble målt hvert 0,1 sekund. Lasting ble
avbrutt før serveren var klar. Egen server ble avsluttet; etterkontrollen fant
ingen gjenværende llama-server-prosess. Dette er et faktisk brudd på tilgjengelig
vertsminne, ikke et RSS-brudd. Det fastslår heller ikke modellens ferdiglastede
RAM-behov eller at modellen ville overskride 4 GiB på en ryddet vert.

## Klargjort og fastsatt før inferens

Den nye generiske instruksjonen og vurderingsmetoden er i
`local_generation_prompt.v1.md` og `local_generation_comparison_protocol.v1.md`.
Den lokale input-frysingen binder alle 25 opprinnelige spørsmål, de tre gamle
tilstrekkelig-konteksttestene, fire omformuleringer av 03/08/17/21 og fire
gjentakelser av 08/17/21/23. Ingen spørsmål ble valgt etter nye svar.

Kontekster og passasjerekkefølge er kopiert fra de forseglede gamle inputene,
uten retrieval, ekstra kilder eller ompakking. Historiske filhashes og alle
25 baseline-/tre diagnostikkforseglinger er kontrollert. Alle 36 inputdefinisjoner
og deres relevante kode-/protokollidentiteter er lagret før modelllasting.

Genereringens inputgrense er 3 200 **faktiske modelltokens**, inkludert native
chat-template, BOS og kontrolltokens. Runtime er 4 096, svarreservasjon 512,
reasoning off, temperatur 0,2, top-p 0,8 og top-k 20. Primære tester bruker seed
42, de fire gjentakelsene seed 43. Samme seed brukes på tvers av kandidatene.
Dette er ikke identisk sampling med den gamle, useedede kontrollen.

Preflight-adapteren bruker lokal loopback-server, ekte system-/brukerroller,
modellens innebygde template, `--no-warmup`, CPU, én slot, ingen context-shift
eller promptcache. `/apply-template` og `/tokenize` skal dokumentere effektiv
input og token-IDer uten inferens; input pluss 512 skal kontrolleres mot både
faktisk slotgrense og modellens kontekstmetadata. Disse kontrollene **ble ikke
nådd**, så verken tokenbudsjett eller effektiv systemrolle er godkjent ennå.
Metoden bygger på [llama.cpp-dokumentasjonen for den installerte revisjonen](https://github.com/ggml-org/llama.cpp/blob/4e7481175/tools/server/README.md).

Tre relevante automatiserte kontroller består: grensekontroll for input/svar
mot faktisk runtime-/modellkontekst, ordrett kildetekst i separate roller og
forhåndsdefinert testutvalg. Dette er ikke en erstatning for runtime-preflight.

## Modellkandidater: dokumentkontroll, ikke full kompatibilitetsgodkjenning

| Kandidat | Verifisert dokumentasjon og variant | Lokal status |
|---|---|---|
| Qwen3.5-2B Q4_K_M | Eksisterende fil, 1 396 198 496 bytes; historisk SHA-256 `57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8` | Lasting avbrutt av verts-RAM; 0 nye svar |
| Qwen3.5-4B Q4_K_M | Qwen originalmodell; Bartowski GGUF `Qwen_Qwen3.5-4B-Q4_K_M.gguf`, publisert størrelse 3,01 GB | Ikke lastet ned eller kjørt |
| Gemma 4 E2B-it QAT Q4_0 | Offisiell Google GGUF `gemma-4-E2B_q4_0-it.gguf`, publisert størrelse 3,35 GB | Ikke lastet ned eller kjørt |

Qwen-originalen og valgt GGUF oppgir Apache 2.0. GGUF-filen er publisert av
Bartowski, ikke av Qwen, og skal etter nedlasting bindes til filens faktiske hash
og bekreftes av runtime. Publisert SHA-256 er
`13c16f426047e2de38cd075bdade4a7bcbc8c774384876f677740cda65f8a983`.
Se [Qwen-originalkortet](https://huggingface.co/Qwen/Qwen3.5-4B) og
[den konkrete GGUF-filen](https://huggingface.co/bartowski/Qwen_Qwen3.5-4B-GGUF/blob/main/Qwen_Qwen3.5-4B-Q4_K_M.gguf).

Google oppgir Apache 2.0, native systemrolle og llama.cpp-bruk for denne QAT-
varianten. E2B-navnet betyr effektive parametre; kortet oppgir 5,1B med embeddings,
så navnet betyr ikke samme lagrings-/RAM-kostnad som Qwen 2B. Ingen multimodal
projektor trengs til den planlagte teksttesten. Google beskriver også egne
mobiloptimaliserte QAT-varianter; de er ikke godkjente erstatninger i denne testen.
Se [Googles modellkort](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf)
og [den konkrete Q4_0-filen](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf/blob/main/gemma-4-E2B_q4_0-it.gguf).

Filstørrelse alene bestemmer ikke peak-RSS. Faktisk runtime-kompatibilitet,
frosne modellrevisjoner/hash etter nedlasting, tokenbudsjett og full ressursmåling
for alle kandidatene gjenstår. Ingen modell er utelatt på grunn av dokumentert
permanent inkompatibilitet; kjøringen stoppet på vertens aktuelle minnetilstand.
Windows-målinger vil uansett ikke dokumentere mobil gjennomførbarhet.

## Historikk og kriterier

Uendret gammel baseline: retrieval 60/72, svar 15/72 og 0/22 komplette svar.
Alle de 15 fulle svarkravene ligger innenfor de 60 retrieval-dekkede kravene;
dermed er 45 av 60 bare delvis gjengitt eller utelatt. Dette er kontrollert per
krav, ikke bare beregnet som differansen mellom to aggregerte scorer.

54/60-målet skal fortsatt beregnes som full svardekning **innenfor** de 60 gamle
retrieval-positive kravene. Kritiske feil/utelatelser når kildene er tilstrekkelige
veier tyngst, og avståelse i alle tre hullene vurderes separat. Krav/gold og
historiske vurderinger er uendret. En modell med bekreftede kritiske feil i de
tilstrekkelige pust/HLR-, anafylaksi- eller vannkontekstene går ikke automatisk
videre på totalscore. Agentgjennomgang er ikke medisinsk sikkerhetsvalidering.

## Bevarte filer og gjenopptakelse

Lokalt: `knowledge/local/diagnostics/local-generation-comparison-v1-2026-10-11/`.
Første tekniske stopp bevares i roten: Windows CRLF-filhash ble feilaktig
sammenlignet med gammel logisk LF-promptidentitet. Korrigeringen i revision-02
verifiserer begge typer identitet og gamle forseglinger, uten kilde-/promptendring
eller ny inferens. Revision-02 inneholder `input-freeze.json`, `stop.json`,
serverkommando, stdout/stderr og ressursmåling. Offentlig audit binder disse
råfilene med hashes uten å publisere kildekontekster eller modeller.

Input-freeze SHA-256:
`31ca5a2179a57f555b2b67c2b4b4154f5f3ad440ccd57a9614d395335a8491f6`.

Neste steg er å frigjøre verts-RAM og deretter gjenoppta preflight eksplisitt.
Ikke slett stoppfilen eller gjenta en stoppet last automatisk. Bevar dette forsøket
og bind neste tekniske forsøk til samme inputdefinisjoner. Full inferensorkestrering,
modellnedlasting og endelig runtime-/modellfrysing gjenstår etter minnekontrollen.
Ingen konklusjon om bedre prompt/modell kan trekkes nå. M2-06 er åpen; holdout,
produksjonskode, M3, gamle modellkall og retrieval-resultater er urørt.
