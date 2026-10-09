"""Offline complete-run audit, preserving the historical phase-B audit."""
import json

import audit_retrieval_optimization_v5 as integrity
import continue_retrieval_phase_c_v1 as c


def audit(public_output=None):
    c.check_frozen()
    raw = integrity.audit(output_paths=[c.STATE / 'raw-integrity-audit.json'])
    plan = c.s.runtime.read(c.d.RUN / 'plan.json')
    layer = c.s.runtime.read(c.LAYER)
    changed = []
    for config in plan['phase_a'] + plan['phase_b'] + plan['phase_c']:
        cid = config['id']
        path = c.d.RUN / 'configurations' / cid / 'summary.json'
        if not path.exists():
            continue
        original = c.s.runtime.read(path)
        old = c.s.runtime.read(c.previous.STATE / 'adjusted' / (cid + '.json'))
        analysis = c.s.runtime.read(c.STATE / 'adjusted' / (cid + '.json'))
        assert analysis['raw_summary_sha256'] == c.d.file_hash(path)
        assert analysis['review_layer_sha256'] == c.d.file_hash(c.LAYER)
        for before, prior, after in zip(original['scores'], old['scores'], analysis['scores'], strict=True):
            expected, ids = c.adjusted(before, layer)
            assert expected == after
            if prior != after:
                fields = [k for k in prior if prior[k] != after[k]]
                assert fields == ['flags']  # Current registered decisions only alter risk.
                assert prior['flags']['contradictory'] == after['flags']['contradictory']
                changed.append({'configuration': cid, 'case_id': before['case_id'], 'cache_key': before['cache_key'],
                                'context_sha256': before['context_sha256'], 'changed_fields': fields, 'records': ids})
        assert analysis['full25'] == c.s.aggregate(analysis['scores'])
        assert analysis['legacy15'] == c.s.aggregate(analysis['scores'], legacy_only=True)
    assert sum(not r['configuration'].startswith('C-') for r in changed) == 6, 'Unexpected historical risk delta'
    assert all(r['case_id'] in ['case-13', 'case-19'] for r in changed)
    result = {**raw, 'phase_C_frozen': True, 'protected_prior_A_B_files': len(c.s.runtime.read(c.STATE / 'freeze.json')['protected_A_B_files']),
              'registered_risk_delta': changed, 'new_review_layer_coverage_changes': 0,
              'limited_owner_B_override': c.s.runtime.read(c.AUTHORIZATION)['limited_override']}
    for path in [c.STATE / 'final-audit.json', public_output or c.s.ROOT / 'evals/retrieval_optimization_final_audit.v2.json']:
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'completed': result['completed_configurations'], 'verified_cases': result['verified_completed_case_inputs'],
                      'integrity_passed': True, 'new_risk_changes': len(changed), 'new_judge_calls': 0}))


if __name__ == '__main__':
    c.s.holdout_guard()
    audit()
