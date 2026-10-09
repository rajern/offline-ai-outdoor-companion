"""Source-free progress/final report for the unchanged resumed B/C experiment."""
from datetime import datetime, timezone
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/experiment'
STATE = RUN / 'continuation-v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def pct(value):
    return '—' if value is None else f'{100 * value:.2f}%'


def export():
    data = read(ROOT / 'evals/retrieval_optimization_results.v4.json')
    # Original frozen accounting follows the active cache slot. Preserve rejected
    # attempts separately when an explicit owner resume archives that slot.
    data['consumption_current_cache'] = deepcopy(data['consumption'])
    data['archived_quota_attempts'] = []
    for path in sorted((STATE / 'quota-retry-archives').glob('*.json')):
        manifest = read(path)
        archive = ROOT / manifest['archive']
        assert archive.resolve().is_relative_to((ROOT / 'knowledge/local/judge-cache-v3').resolve())
        for filename, expected in manifest['file_sha256'].items():
            with (archive / filename).open('rb') as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == expected
        failed = read(archive / 'record.json')
        assert not failed['success'] and failed == manifest['failed_record']
        data['archived_quota_attempts'].append(manifest)
        usage = data['consumption']
        usage['actual_calls'] += 1
        usage['sum_call_seconds'] += failed['elapsed_seconds']
        usage['unknown_usage_calls'] += failed['usage'] is None
        for name, value in (failed['usage'] or {}).items():
            usage['usage'][name] = usage['usage'].get(name, 0) + value
        usage['errors'].append({'cache_key': manifest['cache_key'], 'status': 'archived_quota_rejection',
                                'archive': manifest['archive'], 'validation_errors': failed['validation_errors']})
    data['reported_at'] = datetime.now(timezone.utc).isoformat()
    data['judge_identity'] = read(RUN / 'freeze.json')['judge_identity']
    data['resources_by_worker'] = [dict(file=p.name, **read(p)) for p in sorted((STATE / 'resources').glob('*.json'))]
    resumed = [w for w in data['resources_by_worker']
               if not w['file'].startswith(('retrieve-B-k3-none-', 'score-B-k3-none-'))]
    if resumed:
        data['resumed_worker_resources'] = {
            'workers': len(resumed),
            'peak_process_tree_rss_bytes': max(w['peak_process_tree_rss_bytes'] for w in resumed),
            'minimum_available_ram_bytes': min(w['minimum_available_ram_bytes'] for w in resumed),
            'sum_worker_cpu_seconds': sum(w['cpu_seconds'] for w in resumed)}
    data['resume_attempts'] = [read(p) for p in sorted((STATE / 'resume-attempts').glob('attempt-*.json'))]
    data['indices'] = {p.parent.name: read(p) for p in (RUN / 'indices').glob('*/index.json')}
    data['stage_choices'] = {phase: read(RUN / f'choice-{phase}.json') for phase in ['A', 'B', 'C']
                             if (RUN / f'choice-{phase}.json').exists()}
    data['safety_context_bindings'] = []
    for record in data['configurations']:
        cid = record['configuration']['id']
        if record['status'] != 'complete':
            continue
        adjusted = read(STATE / 'adjusted' / (cid + '.json'))
        rows = {r['case_id']: r for r in read(RUN / 'configurations' / cid / 'retrieved-all.json')}
        for score in adjusted['scores']:
            if score['case_id'] not in ['case-01', 'case-03', 'case-08', 'case-13', 'case-17', 'case-19', 'case-20', 'case-21']:
                continue
            row = rows[score['case_id']]
            data['safety_context_bindings'].append({
                'configuration': cid, 'case_id': score['case_id'], 'decisions': score['decisions'],
                'flags': score['flags'], 'context_sha256': score['context_sha256'], 'cache_key': score['cache_key'],
                'source_items': [{'id': e['item']['id'], 'url': e['item']['source_url']} for e in row['excerpts']],
                'budget_exclusions': [{k: t[k] for k in ['seed_rank', 'seed_id', 'prompt_tokens', 'status']}
                                      for t in row['trace'] if t['status'] == 'over_budget'],
                'certificate_positive': score['certificate_positive'], 'requires_review': score['requires_review']})
    for name in ['final-review.v1.json', 'final-audit.v1.json', 'resume-quota-end.v1.json']:
        if (STATE / name).exists():
            data[name] = read(STATE / name)
    save(ROOT / 'evals/retrieval_optimization_results.v5.json', data)
    records = data['configurations']
    baseline = next(r for r in records if r['configuration']['id'] == 'A-minilm')['adjusted_full25']
    lines = ['# M2-06 — gjenopptatt MiniLM-optimalisering', '',
        f"**Status: {data['status']}. {data['completed']}/31 konfigurasjoner fullstendig vurdert.**", '',
        f"Resultatsnapshot: {data['at']}. Eksport: {data['reported_at']}.", '']
    if data['error']:
        lines += ['Kjøringen stoppet: ' + data['error'], '']
    if 'final-review.v1.json' in data:
        lines += [data['final-review.v1.json']['summary'], '']
    lines += ['## Metode og avgrensning', '',
        'MiniLM er eierens valgte forsøksmodell. Fase A og B-k3-none gjenbrukes; ingen fullførte dommerkall gjentas. '
        'Alle caser bruker den samme frosne kildebasen, V3-prompten, schemaet, scoreren og Codex Sol Medium '
        'gjennom ChatGPT-abonnementet. Ingen betalt API, holdout, Qwen-svargenerering eller produksjonsendring.', '',
        f"Frosset dommeridentitet: `{data['judge_identity']['model']}`, reasoning `{data['judge_identity']['reasoning_effort']}`, "
        f"`{data['judge_identity']['cli_version']}`. Autentisering, modellkatalog og innstillinger kontrolleres før workerens kall. "
        'CLI eksponerer ikke eksakt serverrevisjon; den er fortsatt ukjent, ikke antatt identisk med en vekthash.', '',
        'Case 13/Gemma og case 20/1/MiniLM justeres bare i det separat godkjente, eksakt-input-/kontekstbundne '
        'adjudikasjonslaget. Råresultater og gold er uendret. Justert MiniLM A-baseline: '
        f"{baseline['covered']}/72, micro {pct(baseline['micro_coverage'])}, macro {pct(baseline['macro_coverage'])}, "
        f"{baseline['complete_cases']}/22 komplette. Råbaseline var 56/72 og 14/22; 15-slicen er uendret.", '',
        'Ressursstoppen i den første B-kjøringen er bevart historisk: 5,65 MiB ledig RAM under '
        'score-worker, under 256 MiB-reserven. Alle 25 svarene var lagret og passerte integritetskontroll. '
        'Eieren autoriserte gjenopptakelse med omtrent 3 GiB tilgjengelig RAM. Grenser og eksperimentparametere '
        'ble ikke endret. Etter hver ny worker kontrolleres alle 100 ms-samplede RAM/RSS-målinger.', '',
        'B bruker P2 og k=3/5/8/12/16 × ingen/p10/p30/p50/p70. C bruker P1/P2/P3 med valgt B-kandidat. '
        'Tersklene ble fryst før B fra 400 lagrede, jurisdiksjonsfiltrerte MiniLM top-16-scorer, '
        '`numpy.percentile(method="linear")`; `score >= threshold`. Ingen gold-/judge-tilpasning underveis. '
        'P1/P3-reglene ligger i den opprinnelige frysen; ingen ny LLM eller gold-aware packing.', '',
        'Terskler: ' + ', '.join(f'{k}={v:.8f}' for k, v in data['thresholds']['values'].items()) + '.', '',
        '25-settet: 22 støttede caser / 72 krav og tre separate kunnskapshull. '
        '15-slice: 13 støttede caser / 51 krav og to kunnskapshull. '
        'Uncertain/review blokkerer valg; tom gap-kravliste blir aldri komplett pass. '
        'Den opprinnelige konservative valgregelen beskytter alle dekkede krav og misvisende-/konflikt-/geografifunn per case.', '',
        '## Alle konfigurasjoner', '',
        'Tallene viser justert analyse. Flagg: irrelevant / misvisende / direkte konflikt / geografisk lekkasje på støttede caser.', '',
        '| ID | Status; vurderinger | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | Flagg |',
        '|---|---|---:|---:|---:|---|---|']
    for r in records:
        q, old = r.get('adjusted_full25'), r.get('adjusted_legacy15')
        metrics = '— | — | — | — | —'
        if q:
            metrics = f"{q['covered']}/72 ({pct(q['micro_coverage'])}) | {pct(q['macro_coverage'])} | {q['complete_cases']}/22 | "
            metrics += f"{old['covered']}/51 ({pct(old['micro_coverage'])}) / {pct(old['macro_coverage'])} / {old['complete_cases']}/13 | "
            metrics += ' / '.join(str(q['flags_supported'][f]) for f in ['irrelevant', 'potentially_misleading', 'contradictory', 'jurisdiction_leakage'])
        lines.append(f"| {r['configuration']['id']} | {r['status']}; {r['judged_cases']}/25 | {metrics} |")
    lines += ['', 'Ufullstendige resultater rangeres ikke. Rå/justerte scorer, gap-resultater og sikkerhetens '
        'konteksthash/cache-nøkkel/kilde-ID-er er separat tilgjengelige i `retrieval_optimization_results.v5.json`.', '',
        '## Ressurser og dommerkall', '',
        '2 000 tokens gjelder hele serialiserte grounded prompt med den opprinnelige låste tokenizeren '
        '(samme avgrensning for chat-template-overhead). CPU/RAM er fra denne Windows-maskinen, ikke mobilbenchmark. '
        'Indeksen gjenbrukes; ingen nye embeddingkall i B/C. Worker-CPU inkluderer integritetskontroller; '
        'retrieval+packing inkluderer tokenizerarbeid og har varierende fordel av varm token-cache.', '',
        '| ID | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer | Forkastede pakker | Ranking / retrieval+packing, s |',
        '|---|---:|---:|---:|---:|---:|']
    for r in records:
        m = r.get('resources')
        if m:
            lines.append(f"| {r['configuration']['id']} | {sum(m['prompt_tokens'])/25:.1f} / {max(m['prompt_tokens'])} | "
                f"{sum(m['context_tokens'])/25:.1f} | {sum(m['passages'])} | {m['budget_excluded_packets']} | "
                f"{m['ranking_seconds']:.5f} / {m['retrieval_and_packing_seconds']:.3f} |")
    lines += ['', '| ID | Maks worker-tre RSS, MiB | Min ledig RAM, MiB | Sum worker-CPU, s | Ressursstatus |',
              '|---|---:|---:|---:|---|']
    for r in records:
        cid = r['configuration']['id']
        workers = [w for w in data['resources_by_worker'] if w['file'].startswith(('retrieve-' + cid + '-', 'score-' + cid + '-'))]
        if workers:
            rss = max(w['peak_process_tree_rss_bytes'] for w in workers)
            ram = min(w['minimum_available_ram_bytes'] for w in workers)
            valid = rss <= 4 * 1024**3 and ram >= 256 * 1024**2
            lines.append(f"| {cid} | {rss/1024**2:.1f} | {ram/1024**2:.1f} | "
                f"{sum(w['cpu_seconds'] for w in workers):.2f} | {'består' if valid else 'bevart grensebrudd'} |")
    lines += ['', 'B/C-worker-RSS gjelder gjenbrukt indeks og fjern dommervurdering, ikke hele mobilappen. '
        'MiniLM har 235,05 MB modell og 0,292 MB indeks (384 dimensjoner); '
        'A-indeksarbeidet toppet på omtrent 915 MB prosess-tre-RSS. Gemma har 1 488,92 MB modell / '
        '0,584 MB indeks; Qwen Q4 396,47 MB / 0,778 MB. MiniLMs dokumentvektorer ble gjenbrukt i A, '
        'mens de andre bygget dokumentvektorer; A-indekstidene er derfor ikke en lik full-indeks-benchmark. '
        'MiniLMs kjente 128-token-avkorting (108/405 visninger, ingen spørsmål) er uendret. '
        'Mobil-RAM, energibruk og samlet lokal svartid er fortsatt ikke målt.', '']
    if 'resumed_worker_resources' in data:
        resource = data['resumed_worker_resources']
        lines += [f"Etter gjenopptakelse, eksklusive det historiske B-k3-none-forsøket: "
                  f"maks worker-tre-RSS {resource['peak_process_tree_rss_bytes']/1024**2:.1f} MiB, "
                  f"min ledig RAM {resource['minimum_available_ram_bytes']/1024**2:.1f} MiB, "
                  f"sum målt worker-CPU {resource['sum_worker_cpu_seconds']:.2f} s. "
                  'De opprinnelige 4 GiB/256 MiB-grensene bestod i disse workerne.', '']
    lines += ['Spørsmålsvektorene er også lagrede. Ranking-/packing-tidene inkluderer derfor ikke '
        'embedding av et nytt brukerspørsmål. De er ikke full online retrieval-latens. '
        'Embeddingmålingene fra A og størrelses-/RAMdata rapporteres separat i resultat-JSON.', '']
    usage, before = data['consumption'], data['consumption_before']
    delta = {k: v - before['usage'].get(k, 0) for k, v in usage['usage'].items()}
    lines += ['', f"B/C: {usage['actual_calls']-before['actual_calls']} CLI-kallforsøk, "
        f"{usage['successful_calls']-before['successful_calls']} fullførte vurderinger, "
        f"{usage['cache_hits']-before['cache_hits']} cachetreff/unngåtte kall; tokens `{json.dumps(delta)}`.", '',
        f"Hele A+B/C: {usage['actual_calls']} kall, {usage['successful_calls']} vellykkede; "
        f"tokens `{json.dumps(usage['usage'])}`; {usage['unknown_usage_calls']} med ukjent bruk; "
        f"sum dommerkalletid {usage['sum_call_seconds']:.2f} s. Reasoning inngår i output, prefix-cached input i input; ingen dobbelttelling.", '',
        'Før denne gjenopptakelsen: femtimerskvote 43% brukt, ukeskvote 59% brukt. '
        'Dette er kontoens delte bruk; eval-tokenregnskapet over er separat. Ingen automatisk API-fallback eller kvotereset.', '']
    if data['archived_quota_attempts']:
        lines += [f"{len(data['archived_quota_attempts'])} kvoteavvist forsøk er bevart i et separat hashbundet arkiv "
                  'og inkludert i antall forsøk/ukjent forbruk og kjøretid. Ingen vurdering kom tilbake fra dette forsøket. '
                  'Eierens nye fortsett-instruks kom etter naturlig kvotefornyelse; kun det avviste inputet ble klargjort på nytt. '
                  'Den frosne driverens v4-telling følger nåværende cache; v5 inkluderer også de arkiverte forsøkene.', '']
    if 'resume-quota-end.v1.json' in data:
        end = data['resume-quota-end.v1.json']
        lines += [f"Siste kvotesnapshot {end['at']}: femtimerskvote {end['five_hour_used_percent']}% brukt, "
                  f"ukeskvote {end['weekly_used_percent']}% brukt. "
                  f"Kvoteavvisning under forsøket: {'ja' if end['quota_rejection_occurred'] else 'nei'}. "
                  'En naturlig fornyelse og ny eierinstruks tillot videreføring; ingen reset-kreditt ble brukt.', '']
    if 'final-audit.v1.json' in data:
        audit = data['final-audit.v1.json']
        lines += ['## Teknisk sluttkontroll', '',
                  f"Offline integritetsaudit består: {audit['verified_completed_case_inputs']} case-resultater, "
                  f"{audit['frozen_identity_files_verified']} frosne filer og "
                  f"{audit['phase_a_files_unchanged']} uendrede A-artefakter. "
                  'Kildeproveniens, faktisk kontekst/prompt, token-cache/budsjett, blindet input, '
                  'resultatsegl/loggbruk, schema og kildebevis er kontrollert; rå og justerte aggregater er beregnet på nytt. '
                  'Kun de godkjente eksakte adjudikasjonsbindingene gir justering. Alle tre indeksers vektorhashes og '
                  'det arkiverte kvoteforsøket er verifisert. Ingen nye dommer-/tokenizerkall i audit. '
                  'Dette bekrefter teknisk integritet, ikke uavhengig semantisk sikkerhetsvalidering. '
                  'De tidligere 34 relevante scorer-/packing-/fortsettelsestestene bestod; ny audit-/rapportkode '
                  'har også bestått Python-kompilering og kjøring mot de lagrede resultatene.', '']
    # Detailed source/safety review is supplied separately after the stage gate.
    review = STATE / 'final-review.v1.md'
    if review.exists():
        lines += [review.read_text(encoding='utf-8'), '']
    else:
        lines += ['## Sikkerhet og anbefaling', '',
            'Ingen endelig konfigurasjon anbefales før fase B/C og kilde-/sikkerhetskontroll er ferdige. '
            'Case 01, 03/21, 08, 13, 17 og 20 overvåkes særlig. De kjente manglene i 08/4 og 17/1–2 '
            'må ikke antas løst av parameterendringer. Alle kildepassasjer og dommersvar bevares lokalt.', '']
    lines += ['Historisk B8: 34/51 og 7/13 komplette på den opprinnelige 15-slicen med manuelle vurderinger. '
        'Dette er ikke en kontrollert 25-sett-sammenligning. Forsøket er utviklings-/kalibreringsarbeid, '
        'ikke uavhengig sikkerhetsvalidering. Endelig eierbeslutning og eventuell senere kontrolltest gjenstår.', '',
        'Råtekst, modeller, vektorer og logs er kun lokale og ignorerte. Ingen produksjonsvinner implementeres. M2-06 forblir åpen.', '']
    (ROOT / 'evals/retrieval_optimization_report.v5.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    print(data['status'], data['completed'], '/31; source-free v5 export')
    return data


if __name__ == '__main__':
    export()
