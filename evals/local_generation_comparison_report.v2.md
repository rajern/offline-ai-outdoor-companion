# M2-06: gjenopptatt modell-preflight, 2026-10-24

**Konklusjon:** Qwen 2B er teknisk klar på alle planlagte input. Lasting av
Qwen 4B stoppet deretter på verts-RAM-reserven. Ingen nye svar er generert;
det finnes fortsatt ingen kvalitativ sammenligning eller ny modellvinner.

| Kandidat | Resultat denne gangen | Minimum ledig verts-RAM | Maks prosessgruppe-RSS |
|---|---|---:|---:|
| Qwen3.5-2B Q4_K_M + MiniLM | 36/36 native inputkontroller består | 1 087,68 MiB | 2 570,20 MiB |
| Qwen3.5-4B Q4_K_M + MiniLM | Stopp under lasting | **148,07 MiB** | 3 898,40 MiB |
| Gemma 4 E2B-it offisiell QAT Q4_0 | Ikke lastet ned/kjørt | Ikke målt | Ikke målt |

Grensene er uendret: minst 256 MiB tilgjengelig verts-RAM og høyst 4 GiB
samlet RSS. 4B-stoppet skyldes vertens tilgjengelige RAM, ikke overskridelse
av RSS-grensen. Det beviser ikke at modellen er permanent uegnet for grensen.
Den egne serveren ble avsluttet; etterkontrollen fant ingen gjenværende server.
Det blir ingen automatisk omkjøring etter dette ressursbruddet.

## Det som nå er verifisert

De samme 36 inputdefinisjonene fra 11. oktober er brukt, inklusive fire
omformuleringer og fire gjentakelser valgt før nye svar. Kildetekst, passasjerekkefølge,
spørsmål, prompt og vurderingsprotokoll er uendret. Historiske identiteter og
gamle forseglinger består. Ingen retrieval, ompakking, ny kilde eller endret gold.

2B-kontrollen bruker modellens innebygde chat-template og separate system-/
brukerroller. Systemteksten og hele brukerteksten finnes ordrett i den faktiske
serialiseringen. Den ikke-resonnerende assistant-prefiksen er kontrollert, og
token-IDene er lagret fra modellens egen tokenizer med spesialtokens aktivert.
Alle 36 faktiske input er 777–2 233 tokens. Maksimum pluss 512 reserverte
svartokens er 2 745, innenfor faktisk runtime-slot på 4 096. Genereringens
inputgrense er fortsatt 3 200. GGUF-metadata viser kontekstlengde 262 144;
testen beholder 4 096 og endrer ingen modellgrenser.

Runtime er fortsatt installert build `b11193-4e7481175`. Modellen er samme
2B-fil med SHA-256 `57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8`.
CPU, én server-slot, ingen warmup-inferens, reasoning off, ingen context-shift
eller promptcache. Den faktiske MiniLM-embedderen holdes resident samtidig.

## 4B-filen og uferdige kontroller

Kun den godkjente Qwen-varianten er lastet ned:
`bartowski/Qwen_Qwen3.5-4B-GGUF`, revisjon
`4168f45a16a1290d65a4ec0fa312ae917a4c15d6`,
fil `Qwen_Qwen3.5-4B-Q4_K_M.gguf`, 3 013 027 808 bytes.
Lokal SHA-256 stemmer med publisert filhash:
`13c16f426047e2de38cd075bdade4a7bcbc8c774384876f677740cda65f8a983`.
Hugging Face-metadata oppgir Apache 2.0. Se den
[konkrete GGUF-filen](https://huggingface.co/bartowski/Qwen_Qwen3.5-4B-GGUF/blob/4168f45a16a1290d65a4ec0fa312ae917a4c15d6/Qwen_Qwen3.5-4B-Q4_K_M.gguf).

Det er en Bartowski-kvantisering av Qwen-modellen, ikke en offisiell Qwen GGUF-
utgivelse. Ingen annen variant er valgt. Modellfilen er lokal og ignorert av Git.
Ingen multimodal projektor eller uautorisert modell er lastet ned. 4B kom ikke
til klar server, så dens 36 token-/templatekontroller er uferdige. Gemma er
fortsatt den tidligere godkjente [Google QAT Q4_0-kandidaten](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf), uten ny nedlasting.

## Teknisk adapter og sporbarhet

Det første gjenopptatte forsøket lastet 2B innenfor RAM-grensene, men stoppet
før tokenisering fordi `/props` ikke eksponerer `n_ctx_train` i denne runtime-
versjonen. En liten GGUF-leser i den nye adapteren leser de faktiske scalar-
metadataene, hopper over tokenizerarrayer og leser aldri vekt-tensorene.
Det retter metadatakontrollen uten å endre modellen eller forsøksmetoden.
Første tekniske stopp, oktobers opprinnelige minnestopp og alle råfiler bevares.

`resume_local_generation_v1.py` gjenbruker opprinnelig serveradapter, lås,
ressursvern, filhash- og skrivefunksjoner. Det klargjør også sekvensiell
screening/finalistorkestrering med eksakte preflight-token-IDer, 120 sekunders
genereringsfrist, rårespons/stoppreason, cacheidentitet og forseglinger.
Ingen inferenskode er kjørt eller runtime-godkjent ennå. Før første svar skal
alle kandidatkontroller og den samlede kode-/runtime-/modellfrysingen fullføres.
Den fastsatte svarprotokollen og utvelgelsesreglene skal ikke endres.

Seks relevante enhetstester består: faktisk input/svar-plass, kildebevaring og
roller, forhåndsvalgte tilfeller, native tokenbudsjett, syntetisk GGUF-lesing og
avvisning av endret cachefil. Ingen generell dommertesting eller betalt API.

Lokale råfiler:
`knowledge/local/diagnostics/local-generation-comparison-v1-2026-10-11/resume-2026-10-24/`.
`revision-02/preflight/qwen-2b/` inneholder alle 36 native prompts/token-IDer,
metadata, ressursmåling og seal. `revision-02/preflight/qwen-4b/` inneholder
kommando/stdout/stderr/ressursmåling; `revision-02/stop.json` bevarer minnestoppet.
`revision-02/downloads/qwen-4b/manifest.json` binder modellrevisjon og filhash.
Den offentlige audit v2 publiserer bare identiteter/tall, ikke kildekontekst.

## Hva som gjenstår

Frigjør mer verts-RAM før neste eksplisitte gjenopptakelse. Rundt 5 GiB ledig
før start er et praktisk anslag med margin, ikke en verifisert garanti.
Gjenbruk de beståtte 2B-kontrollene og den verifiserte 4B-filen. Bevar denne
stoppede lasten; ikke slett stoppfiler eller kjør automatisk på nytt.

Deretter gjenstår 4B-/Gemma-preflight, samlet freeze og høyst 33 nye screening-
svar. Finalistens høyst 25 ekstra svar kjøres bare etter de fastsatte kriteriene.
Ingen modell sammenlignes på kvalitetsresultater ennå, og det gamle 15/72-
resultatet er uendret. Ingen oppstart av M3, permanent produksjonsendring,
holdout-tilgang eller ekstra retrieval-eksperimenter.
