"""Verify or restore the public pre-closeout snapshot without running experiments."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'evals/archive/development-2026-10-26.zip'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore-to', type=Path, help='New or empty directory; never overwrite an existing checkout')
    args = parser.parse_args()
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None, 'Damaged archive'
        manifest = json.loads(archive.read('BACKUP-MANIFEST.json'))
        for item in manifest:
            assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256'], item['path']
        for entry in archive.namelist():
            path = PurePosixPath(entry)
            if path.is_absolute() or '..' in path.parts or ':' in entry or '\\' in entry:
                raise ValueError('Unsafe archive entry')
        if args.restore_to:
            destination = args.restore_to.resolve()
            if destination == ROOT or ROOT.is_relative_to(destination):
                raise ValueError('Cannot restore over this project or its ancestors')
            if destination.exists() and any(destination.iterdir()):
                raise ValueError('Destination must be empty')
            destination.mkdir(parents=True, exist_ok=True)
            for entry in archive.namelist():
                target = (destination / entry).resolve()
                if not target.is_relative_to(destination):
                    raise ValueError('Archive path leaves destination')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry))
            print('Restored to:', destination)
        print(f'Verified {len(manifest)} original public project files. No model calls made.')
        print('SHA-256:', hashlib.sha256(ARCHIVE.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
