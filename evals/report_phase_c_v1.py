"""Source-free final development comparison; no model calls or production choice."""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/experiment'
STATE = RUN / 'phase-c-v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def pct(value):
    return '—' if value is None else f'{100 * value:.2f}%'


def export():
    data = read(ROOT / 'evals/retrieval_optimization_results.v6.json')
    data['reported_at'] = datetime.now(timezone.utc).isoformat()
    data['indices'] = read(ROOT / 'evals/retrieval_optimization_results.v5.json')['indices']
    data['safety_context_bindings'] = []
    for entry in data['configurations']:
        if entry['status'] != 'complete':
            continue
        cid = entry['configuration']['id']
        scores = read(STATE / 'adjusted' / (cid + '.json'))['scores']
        rows = {r['case_id']: r for r in read(RUN / 'configurations' / cid / 'retrieved-all.json')}
        for score in scores:
            if score['case_id'] not in ['case-01', 'case-03', 'case-06', 'case-08', 'case-13', 'case-17', 'case-19', 'case-20', 'case-21']:
                continue
            row = rows[score['case_id']]
            data['safety_context_bindings'].append({
                'configuration': cid, 'case_id': score['case_id'], 'decisions': score['decisions'], 'flags': score['flags'],
                'requires_review': score['requires_review'], 'context_sha256': score['context_sha256'], 'cache_key': score['cache_key'],
                'source_items': [{'id': e['item']['id'], 'url': e['item']['source_url']} for e in row['excerpts']],
                'budget_exclusions': [{k: t[k] for k in ['seed_rank', 'seed_id', 'prompt_tokens', 'status']}
                                      for t in row['trace'] if t['status'] == 'over_budget']})
    for name in ['final-review.json', 'final-audit.json', 'quota-end.json']:
        if (STATE / name).exists():
            data[name] = read(STATE / name)
    (ROOT / 'evals/retrieval_optimization_results.v6.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    lines = ['# M2-06 — avsluttende utviklingsrapport', '',
             f"**Status: {data['status']}. {data['completed']}/31 konfigurasjoner ferdige.**", '',
             f"Resultatsnapshot {data['at']}; rapport {data['reported_at']}.", '']
    if data['error']:
        lines += ['Stoppgrunn: ' + data['error'], '']
    review = data.get('final-review.json')
    if review:
        lines += [review['summary'], '']
    lines += ['## Frosset sammenligning og adjudikasjoner', '',
        'A/B ble gjenbrukt. C bruker eierens eksplisitte forsøksvalg MiniLM/k16/ingen terskel og de opprinnelige P1/P2/P3-reglene. '
        'Bare overgangen fra B har et avgrenset eiergodkjent fravik fra dominansregelen. Ingen generell sikkerhetsport er fjernet, '
        'og en automatisk produksjonsvinner blir ikke valgt. Samme 25 spørsmål, kilde-/indekssnapshot, grounded promptserialisering, '
        '2 000-tokenbudsjett, tokenizer, V3-prompt, schema og Sol Codex Medium/ChatGPT gjelder. Ingen betalt API eller svargenerering.', '',
        'Case 13/P70: separat, eksakt inputbundet registrering av potensielt misvisende 113-råd uten dekning. '
        'Case 19/k12 og k16/p30: isredningssekvensen er avgrenset av faktisk levert vann-/is-tekst i source-19-001, '
        'med listen videreført i source-19-002 under samme leverte tittel/tema. Den er irrelevant for skredutstyr, '
        'uten dokumentert feil handling fra en uavgrenset skredinstruks. K12/k16-forskjellen er dommervariasjon; ekstra legevakttekst er ingen '
        'påvist sikkerhetsforbedring. Registreringene skjer under eierens delegerte review-autoritet, ikke som en påstått separat '
        'eiergodkjenning av hvert funn. Bare tre unike hele input korrigeres; identisk cacheinput kan forekomme under flere etiketter. '
        'De gamle godkjente case13/Gemma- og case20/MiniLM-bindingene beholdes separat.', '',
        'Ingen råresultater, fasit, prompt, bevisregler eller P3-regler er overskrevet. '
        'Nye C-kontekster arver ikke historiske rettelser uten samme komplette inputidentitet. '
        'Uavklart betydning/risiko markeres review og hindrer automatisk valg. '
        '25-settet har 22 støttede caser/72 krav og tre kunnskapshull; 15-slicen har 13 støttede caser/51 krav og to hull. '
        'Tom gap-kravliste gir aldri automatisk komplett pass.', '',
        '## Alle 31 konfigurasjoner', '',
        'Justert analyse. Flagg er antall støttede caser med irrelevant / potensielt misvisende / direkte konflikt / geografisk lekkasje.', '',
        '| ID | Status | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | Flagg |',
        '|---|---|---:|---:|---:|---|---|']
    for row in data['configurations']:
        q = row.get('adjusted_full25')
        if q:
            old = row['adjusted_legacy15']
            metrics = f"{q['covered']}/72 ({pct(q['micro_coverage'])}) | {pct(q['macro_coverage'])} | {q['complete_cases']}/22 | "
            metrics += f"{old['covered']}/51 ({pct(old['micro_coverage'])}) / {pct(old['macro_coverage'])} / {old['complete_cases']}/13 | "
            metrics += ' / '.join(str(q['flags_supported'][f]) for f in ['irrelevant', 'potentially_misleading', 'contradictory', 'jurisdiction_leakage'])
        else:
            metrics = '— | — | — | — | —'
        lines.append(f"| {row['configuration']['id']} | {row['status']}; {row['judged_cases']}/25 | {metrics} |")
    lines += ['', '## Ressurser og tokens', '',
        '| Oppsett | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer / forkastede pakker | Ranking / packing, s | Maks RSS / min ledig RAM, MiB | Worker-CPU, s |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for row in data['configurations']:
        cid = row['configuration']['id']
        if cid != 'B-k16-none' and not cid.startswith('C-'):
            continue
        resource = row.get('resources')
        if not resource:
            continue
        workers = [w for w in data['resources_by_worker'] if w['file'].startswith(('retrieve-' + cid + '-', 'score-' + cid + '-'))]
        memory = '—'
        cpu = '—'
        if workers:
            memory = f"{max(w['peak_process_tree_rss_bytes'] for w in workers)/1024**2:.1f} / {min(w['minimum_available_ram_bytes'] for w in workers)/1024**2:.1f}"
            cpu = f"{sum(w['cpu_seconds'] for w in workers):.2f}"
        lines.append(f"| {cid} | {sum(resource['prompt_tokens'])/25:.2f} / {max(resource['prompt_tokens'])} | "
            f"{sum(resource['context_tokens'])/25:.2f} | {sum(resource['passages'])} / {resource['budget_excluded_packets']} | "
            f"{resource['ranking_seconds']:.5f} / {resource['retrieval_and_packing_seconds']:.3f} | {memory} | {cpu} |")
    lines += ['', 'Ranking/packing bruker lagrede spørsmålsvektorer og inkluderer ikke embedding av et nytt spørsmål. '
        'Token-cache påvirker packing-tiden; worker-CPU inkluderer kontroller og tokenizerarbeid. Målingene er fra denne Windows-maskinen, '
        'ikke en mobilbenchmark. MiniLM-modell 235,05 MB, indeks 0,292 MB / 384 dimensjoner; modell/index endres ikke med packing. '
        'A viste omtrent 915 MB prosess-tre-RSS ved indeksarbeid; MiniLM dokumentvektorer var gjenbrukt. '
        'Gemma/Qwen har egne, ikke like full-indekstidsmålinger; detaljer beholdes i historisk v5 og resultat-JSON. '
        '128-token embeddingavkorting og dens dokumenterte eksponering beholdes; ingen kontrafaktisk rangeringstest er kjørt. '
        'Ressursgrenser: 256 MiB tilgjengelig RAM og 4 GiB prosess-tre-RSS, samplet hvert 100 ms og kontrollert før/etter worker. '
        'Mobilminne, energibruk og full online latens er ikke målt.', '']
    usage, before = data['consumption'], data['consumption_before_C']
    delta = {k: value - before['usage'].get(k, 0) for k, value in usage['usage'].items()}
    lines += [f"C: {usage['actual_calls']-before['actual_calls']} CLI-kallforsøk, "
              f"{usage['successful_calls']-before['successful_calls']} fullførte nye vurderinger, "
              f"{usage['cache_hits']-before['cache_hits']} cachetreff; rapporterte tokens `{json.dumps(delta)}`.", '',
              f"Samlet A+B+C: {usage['actual_calls']} forsøk, {usage['successful_calls']} fullførte, "
              f"{usage['cache_hits']} cachetreff, {usage['unknown_usage_calls']} med ukjent tokenbruk; "
              f"rapporterte tokens `{json.dumps(usage['usage'])}`; sum kalltid {usage['sum_call_seconds']:.2f} s.", '',
              'Reasoning inngår i output, prefix-cached input i input. Det historiske kvoteavviste forsøket er bevart og medregnet '
              'med ukjent bruk; ingen estimert nullbruk eller API-kostnad. CLI-serverrevisjon eksponeres ikke, mens forespurt/katalogmodell '
              'gpt-6.1-sol, Medium, CLI-versjon og abonnementsauth er frosset og kontrollert. Kvoter gjelder den delte kontoen.', '']
    if 'quota-end.json' in data:
        quota = data['quota-end.json']
        lines += [f"Siste kvote {quota['at']}: 5t {quota['five_hour_used_percent']}% brukt, uke {quota['weekly_used_percent']}% brukt. "
                  'Ingen betalt API-fallback eller reset-kreditt.', '']
    if 'final-audit.json' in data:
        audit = data['final-audit.json']
        lines += [f"Offline sluttkontroll består: {audit['verified_completed_case_inputs']} case-resultater, "
                  f"{audit['frozen_identity_files_verified']} frosne identitetsfiler og "
                  f"{audit['protected_prior_A_B_files']} bevarte A/B-filer. Kildeproveniens, full serialisering/token-cache, "
                  'input-/resultatsegl, schema, kildebevis, raw/justerte aggregater og registrerte risikodelta er kontrollert uten nye dommerkall. '
                  'Seks nye C-kontrolltester og ni eksisterende fortsettelsestester bestod. Integritet er ikke uavhengig sikkerhetsvalidering.', '']
    review_path = STATE / 'final-review.md'
    if review_path.exists():
        lines += [review_path.read_text(encoding='utf-8'), '']
    else:
        lines += ['Endelig kilde-/sikkerhetsgjennomgang og anbefaling er ennå ikke ferdig.', '']
    lines += ['Historisk manuell B8: 34/51, 7/13 komplette på opprinnelige 15 spørsmål. '
        'Endret dommer gjør dette til historisk referanse, ikke kontrollert effektmåling mot dagens 25-sett. '
        'Utviklingssettet brukes til kalibrering/valg; holdout er ikke åpnet eller kjørt. '
        'Råtekst, modeller, indekser og logger beholdes lokalt. Ingen produksjonskonfigurasjon eller Qwen-svargenerering er endret. '
        'M2-06 forblir åpen for senere produkt-/sikkerhetsarbeid.', '']
    (ROOT / 'evals/retrieval_optimization_report.v6.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    print(data['status'], data['completed'], '/31')


if __name__ == '__main__':
    export()
