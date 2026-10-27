"""Check the curated reading path and replay provenance; no model/network calls."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    files = [ROOT/name for name in ('README.md','TASKS.md','evals/README.md','backend/README.md','frontend/README.md')]
    files += list((ROOT/'docs').glob('*.md'))
    missing = []
    for path in files:
        for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8-sig')):
            link = link.strip('<>').split('#')[0]
            if not link or re.match(r'[a-z]+:', link):
                continue
            if not (path.parent/link).exists():
                missing.append(f'{path.relative_to(ROOT)}: {link}')
    if missing:
        raise ValueError('Missing active links:\n'+'\n'.join(missing))
    examples = json.loads((ROOT/'frontend/demo/examples.json').read_text(encoding='utf-8'))
    provenance = json.loads((ROOT/'frontend/demo/provenance.json').read_text(encoding='utf-8'))
    private_checks = 0
    for example, record in zip(examples, provenance, strict=True):
        assert example['id'] == record['case_id']
        assert all(s['license'] and s['url'].startswith('https://') and s['notice'] for s in example['response']['sources'])
        ids = [e['id'] for s in example['response']['sources'] for e in s['excerpts']]
        assert len(ids) == len(set(ids)) and set(ids) == set(record['excerpt_ids'])
        original = ROOT/record['answer_path']
        if original.is_file():
            assert hashlib.sha256(original.read_bytes()).hexdigest() == record['answer_sha256']
            assert original.read_text(encoding='utf-8') == example['response']['answer']
            private_checks += 1
    # Selected final evaluation evidence must still have its original bytes.
    archive = ROOT/'evals/archive/development-2026-10-26.zip'
    inventory = json.loads((ROOT/'evals/archive/index.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == inventory['archive_sha256']
    with zipfile.ZipFile(archive) as source:
        manifest = {v['path']:v for v in json.loads(source.read('BACKUP-MANIFEST.json'))}
        preserved = 0
        for name in inventory['retained_evals']:
            if name in ('AGENTS.md','README.md'):
                continue
            path = ROOT/'evals'/name
            assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest[path.relative_to(ROOT).as_posix()]['sha256'], name
            preserved += 1
    print(f'Passed: {len(files)} curated Markdown files,2 replay packages,{private_checks} private answer checks,{preserved} unchanged final evidence files.')
    print('Historical inline links require archive restoration; they are intentionally excluded from the active reading-path check.')


if __name__ == '__main__':
    main()
