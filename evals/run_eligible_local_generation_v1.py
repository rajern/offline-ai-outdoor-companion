"""Continue remaining approved models after a proven 4 GiB candidate exclusion."""
import continue_local_generation_v1 as c

RUN = c.r.p.ROOT / 'knowledge/local/diagnostics/local-generation-eligible-2026-10-24'
RSS_ATTEMPT = c.r.p.ROOT / 'knowledge/local/diagnostics/local-generation-comparison-retry02-2026-10-24'


def install():
    c.RETRY = RUN
    c.inherit()
    resource_path = RSS_ATTEMPT / 'preflight/qwen-4b/resources.json'
    measured = c.r.q.read(resource_path)
    assert measured['minimum_available_ram_bytes'] >= c.r.RAM_RESERVE
    assert measured['peak_process_tree_rss_bytes'] > c.r.RSS_LIMIT
    c.r.q.write_once(RUN / 'exclusions.json', {'qwen-4b': {
        'reason': 'Proven process-group RSS >4 GiB with host reserve intact; frozen protocol permits exclusion',
        'resource_path': str(resource_path), 'resource_sha256': c.r.q.sha(resource_path),
        'model_sha256': c.r.q.sha(c.r.MODELS['qwen-4b']['path']),
        'settings_unchanged': True, 'no_inference': True}})
    c.r.RUN = RUN


if __name__ == '__main__':
    c.r.q.t.s.holdout_guard()
    install()
    c.r.main()
