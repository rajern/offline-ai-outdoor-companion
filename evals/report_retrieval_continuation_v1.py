"""Source-free Norwegian B/C report from saved results. No retrieval/inference."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/experiment'
STATE = RUN / 'continuation-v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def percent(value):
    return '—' if value is None else f'{100 * value:.1f}%'


def report():
    data = read(ROOT / 'evals/retrieval_optimization_results.v4.json')
    records = data['configurations']
    lines = ['# M2-06 — MiniLM fase B/C', '',
             f"Status: **{data['status']}**, {data['completed']}/31 konfigurasjoner fullført.", '']
    if data['error']:
        lines += ['Kjøringen stoppet: ' + data['error'], '']
    if data['status'] == 'blocked':
        lines += ['**B-k3-none er fullstendig vurdert, men består ikke ressurskontrollen.** '
            'Ledig RAM falt til 5,65 MiB under score-workerens kjøring, under reserven på 256 MiB. '
            'Score-workerens prosess-tre toppet på 230,2 MiB RSS; RSS-grensen på 4 GiB ble ikke brutt. '
            'Tallene nedenfor er bevarte diagnostiske resultater, ikke en teknisk godkjent kandidat. '
            '24 B- og tre C-konfigurasjoner gjenstår. Stopp skjedde ved kontrollen etter score-worker; '
            'alle 25 resultater var da lagret. Målingen identifiserer ikke hvilken annen prosess som brukte RAM.', '']
    lines += ['## Adjudikasjoner og metode', '',
        'Eieren valgte MiniLM til forsøket 2026-10-09. Case 13/Gemma flagges som potensielt misvisende, '
        'uten direkte konflikt. Case 20/1/MiniLM godtas som semantisk dekning. '
        'Det godkjente v1-laget binder hver beslutning til case, levert konteksthash og full dommerinput/cache-nøkkel. '
        'Bare identisk input kan arve beslutningen i B/C. Nye kontekster får ingen automatisk adjudikasjon.', '',
        'Alle 75 A-resultater og cacheforseglinger ble kontrollert uten nye dommerkall. '
        'Delta-kontrollen fant bare case 20s dekning/beslutning og case 13s flagg. '
        'Originale svar, scorer, gullkrav, prompt, corpus og fase A-filer beholdes uendret. '
        'MiniLM-baselinen er rått 56/72, 75,68% macro og 14/22 komplette; '
        'justert 57/72 (79,17%), 77,95% macro og 15/22 komplette. Den historiske 15-slicen endres ikke.', '',
        'Videreføring bruker eksisterende workers, MiniLM-indeks og eksakt-input-cache, '
        'eksklusiv eksperiment-/dommerlåsing og feiljournal. 34 relevante automatiske tester består '
        '(9 fortsettelse, 13 orkestrering, 12 scorer/packing). Ingen fase A-modellkall er gjentatt. '
        'De 28 planlagte kombinasjonene og original packing/scoring er uendret.', '']
    audit = ROOT / 'evals/retrieval_optimization_continuation_audit.v1.json'
    if audit.exists():
        a = read(audit)
        lines += [f"Sluttaudit: {a['frozen_identity_files_verified']} frosne identitetsfiler kontrollert, "
            f"{a['phase_a_files_unchanged']} A-filer uendret, alle 25 B-kontekst-/prompt-/token-/cachebindinger kontrollert. "
            'Ingen nye dommerkall i audit. Integriteten består; ressursporten består ikke. '
            'Se `retrieval_optimization_continuation_audit.v1.json` for eksakte SHA- og kilde-ID-bindinger.', '']
    if data['thresholds']:
        lines += ['Terskler, fryst før B: ' + ', '.join(f'{k}={v:.8f}' for k, v in data['thresholds']['values'].items()) + '. '
            '400 jurisdiksjonsfiltrerte top-16-scorer fra lagrede A-minilm-resultater; '
            '`numpy.percentile(method="linear")`, inklusiv grense (`score >= threshold`).', '']
    lines += ['## Alle konfigurasjoner', '',
        '25-settet har 22 støttede caser / 72 krav og tre separate kunnskapshull. '
        '15-slicen har 13 støttede caser / 51 krav og to kunnskapshull. Tabellen viser justert analyse. '
        'Flaggkolonnen er irrelevant / potensielt misvisende / direkte konflikt / geografisk lekkasje på støttede caser.', '',
        '| Konfigurasjon | Status / vurdert | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | Flagg |',
        '|---|---|---:|---:|---:|---|---|']
    for row in records:
        q, old = row.get('adjusted_full25'), row.get('adjusted_legacy15')
        cid = row['configuration']['id']
        if q is None:
            values = '| — | — | — | — | — |'
        else:
            flags = q['flags_supported']
            values = f"| {q['covered']}/72 ({percent(q['micro_coverage'])}) | {percent(q['macro_coverage'])} | {q['complete_cases']}/22 | "
            values += f"{old['covered']}/51 ({percent(old['micro_coverage'])}) / {percent(old['macro_coverage'])} / {old['complete_cases']}/13 | "
            values += ' / '.join(str(flags[k]) for k in ['irrelevant', 'potentially_misleading', 'contradictory', 'jurisdiction_leakage']) + ' |'
        lines.append(f"| {cid} | {row['status']} / {row['judged_cases']}/25 " + values)
    lines += ['', 'Rå og justerte 25-/15-aggregater, casevise beslutninger, review og tokens er separat lagret i '
        '`retrieval_optimization_results.v4.json`. Ufullførte konfigurasjoner får ingen full-sett-score eller rangering.', '',
        '## Ressurser og Codex-bruk', '',
        'Grensene er uendret: 2 000 tokens for komplett grounded prompt, med original serialisering og låst tokenizer; '
        '256 MiB ledig-RAM-reserve og 4 GiB samtidig prosess-tre-RSS. Alle workers kjøres sekvensielt. '
        'Tokenizer brukes bare til telling; ingen Qwen-svar genereres.', '',
        '| Konfigurasjon | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer totalt | Forkastede pakker | Ranking / retrieval+packing (s) |',
        '|---|---:|---:|---:|---:|---:|']
    for row in records:
        r = row.get('resources')
        if not r:
            continue
        lines.append(f"| {row['configuration']['id']} | {sum(r['prompt_tokens'])/25:.1f} / {max(r['prompt_tokens'])} | "
            f"{sum(r['context_tokens'])/25:.1f} | {sum(r['passages'])} | {r['budget_excluded_packets']} | "
            f"{r['ranking_seconds']:.5f} / {r['retrieval_and_packing_seconds']:.3f} |")
    resource_records = [read(p) for p in sorted((STATE / 'resources').glob('*.json'))]
    if resource_records:
        lines += ['', f"B/C-workers: høyeste observerte prosess-tre-RSS {max(r['peak_process_tree_rss_bytes'] for r in resource_records)/1024**2:.1f} MiB, "
            f"laveste ledige RAM {min(r['minimum_available_ram_bytes'] for r in resource_records)/1024**2:.1f} MiB; "
            f"sum observert CPU {sum(r['cpu_seconds'] for r in resource_records):.2f} s. Sampling 100 ms.",
            'Retrieval+packing inkluderer tokenizer/cache-arbeid; gjentatte kontekster får fordel av varm cache. '
            'Dette er Windows-målinger, ikke mobilbenchmark.', '']
    index = read(RUN / 'indices/minilm/index.json')
    lines += [f"MiniLM: {index['model_size_bytes']/1e6:.2f} MB modell, {index['index_size_bytes']/1e6:.3f} MB indeks, "
        f"{index['dimensions']} dimensjoner. Eksisterende indeks gjenbrukes; intet nytt embeddingkall i B/C. "
        'Den kjente trunceringen ved 128 tokens er uendret (108/405 dokument-/spørsmålsvisninger; ingen spørsmål trunkert).', '']
    usage, before = data['consumption'], data['consumption_before']
    delta_calls = usage['actual_calls'] - before['actual_calls'] if before else usage['actual_calls']
    delta_usage = {k: v - (before or {}).get('usage', {}).get(k, 0) for k, v in usage['usage'].items()}
    lines += [f"B/C: {delta_calls} faktiske nye dommerkall; {usage['cache_hits'] - (before or {}).get('cache_hits', 0)} cachetreff/unngåtte kall. "
        f"Rapporterte nye tokens: `{json.dumps(delta_usage)}`.", '',
        f"Hele A+B/C: {usage['actual_calls']} faktiske kall, {usage['successful_calls']} vellykkede; "
        f"{usage['unknown_usage_calls']} med ukjent bruk. Tokens: `{json.dumps(usage['usage'])}`.",
        'Reasoning er del av output og prefix-cached input del av input; disse legges ikke til totalen på nytt. '
        f"Sum dommerkalletid {usage['sum_call_seconds']:.2f} s. GPT-6.1 Sol / Codex CLI / Medium / ChatGPT-abonnement; betalte API-kall: 0.", '']
    if usage['errors']:
        lines += ['Feil: `' + json.dumps(usage['errors']) + '`.', '']
    quota = STATE / 'quota-snapshots.json'
    if quota.exists():
        q = read(quota)
        lines += [f"Codex-kvote før B: {q['before_phase_b']['five_hour_used_percent']}% brukt i femtimersvinduet og "
            f"{q['before_phase_b']['weekly_used_percent']}% i ukesvinduet. Etter stoppen: "
            f"{q['after_memory_stop']['five_hour_used_percent']}% / {q['after_memory_stop']['weekly_used_percent']}%. "
            'Ingen kvotegrense var nådd. Dette er kontoens delte forbruk; prosentendringen kan ikke tilskrives B alene.', '']
    lines += ['## Sikkerhet og anbefaling', '',
        'Krav som følges spesielt: 01 brudd/lege, 03 og 21 vannbehandling, 08 luftvei/pust/overvåking/HLR, '
        '13 nødpeiler uten mobildekning, 17 anafylaksi/akutt eskalering, 20 rute/ferdigheter. '
        'Tidligere kilde-/ranganalyse viser at full dekning av 08/4 og 17/1–2 ikke er tilgjengelig '
        'gjennom MiniLMs frosne top-16/P1/P3-regler. Dette forsøket kan derfor ikke alene gjøre løsningen tilstrekkelig trygg.', '']
    if any(r['configuration']['id'] == 'B-k3-none' and r['status'] == 'complete' for r in records):
        lines += ['### Første B-resultat mot justert MiniLM-baseline', '',
            'Dekningen faller fra 57/72 til 40/72: **−17 krav**, micro **−23,61 prosentpoeng**, '
            'macro **−22,73 prosentpoeng**, komplette **15 → 8**. Ingen nye dekkede krav etter godkjent A-justering. '
            '15-slicen faller fra 39/51 til 25/51 (76,47% → 49,02%), macro 74,23% → 44,74%, '
            'komplette 8 → 3. Irrelevant-flagg faller 22 → 20; misvisende øker 1 → 2; '
            'direkte konflikt og geografi forblir 0. Ingen uncertain, review eller sertifikat-/dommeruenighet.', '',
            'De 17 tapene er 01/4; 05/3,6; 07/1–4; 08/1; 10/2,3; 11/1,2; 12/1,2; 19/1; 23/2,3. '
            'Ingen pakker ble forkastet på tokenbudsjett i B-k3-none. Passasjer som ligger utenfor de tre '
            'første kandidatene blir ikke levert; det er dermed k-grensen, ikke en ny embedding eller '
            'budsjettforkasting, som endrer konteksten. Den eldre MiniLM-trunceringen er fortsatt en separat begrensning.', '',
            '| Case | Udekket i B-k3-none | Levert grunnlag / konsekvens |',
            '|---|---|---|',
            '| 01 | 1–4: bruddmistanke, skille brudd/forstuing, legekontakt, ro/avlastning | Bare 19-004, 19-003 og 10-004; A dekket kun 01/4. Ingen bruddpassasje levert. |',
            '| 03 | 3–5: full kokeprosedyre med høydebetingelser og kjemisk begrensning/alternativ kilde | 21-005 og 21-002 dekker klart/usikkert vann; 21-010 og 21-009 mangler fortsatt. |',
            '| 08 | 1,2,4: 113 med veiledning; komplett luftvei/pustesjekk; overvåking/HLR/113 ved tvil | 07-003, 07-006, 01-010; bare sideleiekravet 08/3 fullt dekket. 08/1 er nytt tap mot A. Cachetreffet gjelder en eldre input, ikke A-baselinen. |',
            '| 13 | 1–2: tidlig nødpeileraktivering og aktivering ved tvil | 01-027, 04-009, 03-008 leverer telefoninstruksjoner uten dekning; risiko beholdes. 11-003 mangler. |',
            '| 17 | 1–2: symptom-/insektkobling og umiddelbar akutt eskalering | 17-003, 19-002, 05-003; ingen relevant full anafylaksipassasje. |',
            '| 20 | Ingen av de to kravene mangler | 16-002 støtter rute/evner, 10-003 været. Ny dommerinput fikk begge krav covered uten overføring av A-adjudikasjonen. |',
            '| 21 | 2: produktinstruksjoner som del av hele filtrer/desinfiser-kravet | 21-011 gir virusbegrensning og rekkefølge; 21-009 med produktforbehold mangler. |', '',
            'Fortsatt udekkede krav på alle 22 støttede caser: '
            '01/1–4; 03/3–5; 05/3,6; 06/1,4; 07/1–4; 08/1,2,4; 10/2,3; '
            '11/1,2; 12/1,2; 13/1,2; 17/1,2; 19/1; 21/2; 23/2,3. '
            'Dette er 32 av 72 krav. De tre kunnskapshullene behandles fortsatt separat; '
            '14 har bare 1/2 støtte, 15 og 25 har tom kravliste og aldri komplett pass.', '',
            '### Det nye sikkerhetsflagget i case 19', '',
            'Dommeren flagger **source-19-002, blokk 3** som både irrelevant og potensielt misvisende: '
            'isredningsråd om grein/stige/menneskekjede kan oppfattes som skredredning. '
            'I faktisk levert tekst står bare den generelle tittelen «Redning» og temaet «Redde andre»; '
            'situasjonen med is er ikke merket i denne blokken. Risikoen er derfor konkret og forenlig '
            'med V2-regelen om å skille irrelevans fra mulig feil handling. Direkte konflikt er ikke flagget. '
            'Den samme blokken finnes i A, som også leverer ekstra skred-/utstyrstekst og en eksplisitt '
            'Isskolen-blokk. Uten nye dommerkall kan vi ikke skille konteksteffekt fra dommervariasjon. '
            'Det nye risikoflagget beholdes, uten automatisk adjudikasjon. '
            'Den manglende konkrete utstyrslisten (17-001, A-blokk 6) er et separat sikkerhetskritisk tap.', '',
            'Senere forbedringer utenfor dagens plan bør særlig undersøke rangeringen for 08/4 og '
            '17/1–2, MiniLMs 128-token-avkorting og bevaring av situasjonsvilkår i kildepassasjer. '
            'Kildene finnes allerede lokalt; dette er ikke grunnlag for å legge til nye kilder eller '
            'endre gold. B/C må fullføres før andre parametervarianter vurderes.', '']
    chosen = RUN / 'choice-C.json'
    if data['status'] == 'complete' and chosen.exists():
        lines += ['Foreløpig anbefaling etter den frosne valgregelen: `' + json.dumps(read(chosen)['configuration']) + '`. '
                  'Dette er ingen produksjonsimplementering eller selvstendig sikkerhetsvalidering.', '']
    else:
        lines += ['Ingen endelig B/C-konfigurasjon kan anbefales fra denne ufullførte kjøringen. '
                  'MiniLM er fortsatt eierens valgte forsøksmodell; A-baseline er referansen. '
                  'Top_k=3 uten terskel/P2 gir klart svakere dekning og ett ekstra sikkerhetsflagg og '
                  'anbefales ikke fremfor den justerte k=8-baselinen. Dette er ingen endelig rangering '
                  'av de 27 uprøvde konfigurasjonene. En reell blokkering må avklares før resten gjenopptas.', '',
                  'Etter at tilstrekkelig RAM er tilgjengelig igjen, kan samme fortsettelseskommando '
                  'gjenbruke den komplette B-k3-none-scoringen og fortsette ved B-k3-p10. '
                  'Ingen av de 22 nye dommerkallene eller 75 A-kallene skal gjentas. '
                  'Minnegrensen, tersklene og øvrige frosne innstillinger beholdes.', '']
    lines += ['Historisk B8 hadde 34/51 krav og 7/13 komplette på 15-settet med andre manuelle vurderinger. '
        'Dette er historisk kontekst, ikke en kontrollert effekt mot dagens 25-sett.', '',
        'Råkontekster, kildepassasjer, vektorer, token-/dommercache og logs bevares lokalt under '
        '`knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/` og `knowledge/local/judge-cache-v3/`. '
        'Den offentlige rapporten inneholder ikke kildetekst, modeller eller hemmeligheter. '
        'Holdout er ikke åpnet. Produksjonskonfigurasjonen er uendret. M2-06 forblir åpen.', '']
    (ROOT / 'evals/retrieval_optimization_report.v4.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    report()
