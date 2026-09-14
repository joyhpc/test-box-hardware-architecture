"""Portable publication hygiene checks, not a substitute for content review."""
import re
import json
from pathlib import Path
from validate_source_manifest import validate

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', 'dist', '__pycache__', '.local'}


def check_publication():
    manifest = ROOT / 'test-box-hardware-architecture/examples/source-manifest.json'
    try:
        errors = validate(json.loads(manifest.read_text(encoding='utf-8')))
    except (OSError, ValueError) as exc:
        errors = [f'public manifest unreadable: {type(exc).__name__}']
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in IGNORED for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix not in ('.md', '.json', '.py', '.yml', '.yaml', '.txt'):
            continue
        text = path.read_text(encoding='utf-8')
        relative = path.relative_to(ROOT).as_posix()
        if re.search(r'\b[A-Za-z]:[\\/]', text) or re.search(r'/(?:Users|home)/[^\s/]+/', text):
            errors.append(f'{relative}: machine-specific absolute path')
        if re.search(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b', text):
            errors.append(f'{relative}: credential-shaped value')
    return errors


if __name__ == '__main__':
    import json
    errors = check_publication()
    print(json.dumps({'errors': errors, 'scope': 'Generic paths, manifest shape and common credential format only; manual content review required.'}, indent=2))
    raise SystemExit(bool(errors))
