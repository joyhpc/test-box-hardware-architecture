"""Build a verified ZIP; optionally install into a NEW explicitly chosen directory."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'test-box-hardware-architecture'
VERSION = '1.1.0'


def fingerprint(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, help='New install directory; existing directories are never overwritten')
    args = parser.parse_args()
    archive = ROOT / 'dist' / f'{SOURCE.name}-v{VERSION}.zip'
    if archive.exists():
        raise SystemExit('Archive exists; do not overwrite a release. Choose a new version in source.')
    if args.target and args.target.exists():
        raise SystemExit('Existing installation preserved. Choose a new empty target explicitly.')
    for command in [
        [sys.executable, '-X', 'utf8', 'tools/check_package.py'],
        [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'test-box-hardware-architecture/evals', '-p', 'test_*.py', '-v'],
    ]:
        subprocess.run(command, cwd=ROOT, check=True)
    hashes = fingerprint(SOURCE)
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as package:
        for relative in hashes:
            package.write(SOURCE / relative, f'{SOURCE.name}/{relative}')
    with zipfile.ZipFile(archive) as package:
        archived = {name[len(SOURCE.name) + 1:]: hashlib.sha256(package.read(name)).hexdigest() for name in package.namelist()}
        if package.testzip() is not None or archived != hashes:
            raise SystemExit('Archive integrity/content mismatch')
    installed = False
    if args.target:
        shutil.copytree(SOURCE, args.target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if fingerprint(args.target) != hashes:
            raise SystemExit('New installation content mismatch; inspect before use')
        installed = True
    report = dict(version=VERSION, file_count=len(hashes), source_archive_identical=True,
                  archive=archive.relative_to(ROOT).as_posix(),
                  archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                  installation='NEW_TARGET_VERIFIED' if installed else 'NOT_UPDATED_EXISTING_COPY_PRESERVED',
                  client_discovery='NOT_TESTED', fingerprint_scope='Only this public skill package, never private hardware sources',
                  files=hashes)
    (ROOT/'reports/installation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({key:value for key,value in report.items() if key!='files'}, indent=2))


if __name__ == '__main__':
    main()
