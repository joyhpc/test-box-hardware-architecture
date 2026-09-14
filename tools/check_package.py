"""Check package links, JSON, portable entry point and evaluation records."""
import json
import re
from pathlib import Path
from check_publication import check_publication

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'test-box-hardware-architecture'
errors = []
errors.extend(check_publication())
files = [p for p in SKILL.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
for path in files:
    if path.suffix in ('.md', '.json', '.yaml', '.py'):
        try:
            decoded = path.read_text(encoding='utf-8')
            if '\ufffd' in decoded:
                errors.append(f'{path.name}: replacement character in text')
        except UnicodeDecodeError:
            errors.append(f'{path.name}: text is not UTF-8')
            continue
    if path.suffix == '.json':
        try:
            json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            errors.append(f'{path.name}: {exc}')
    if path.suffix == '.md':
        content = path.read_text(encoding='utf-8')
        if '[TODO:' in content:
            errors.append(f'{path.name}: initializer placeholder remains')
        for target in re.findall(r'\]\(([^)]+)\)', content):
            target = target.split('#')[0].replace('%20', ' ')
            if not target or re.match(r'^[a-zA-Z]+:', target) or target.startswith('/'):
                continue
            if not (path.parent / target).exists():
                errors.append(f'{path.relative_to(ROOT)}: broken link {target}')
entry = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
metadata = (SKILL / 'agents/openai.yaml').read_text(encoding='utf-8')
if '$test-box-hardware-architecture' not in metadata:
    errors.append('default prompt does not name the skill')
if len(entry.splitlines()) > 150:
    errors.append('entry point exceeds 150-line maintenance target')
if re.search(r'[CD]:[\\/]', entry):
    errors.append('entry point contains machine-specific dependency')
required = ['SKILL.md', 'README.md', 'references/top-down.md', 'references/sizing.md', 'references/modules-planes.md',
            'references/interfaces.md', 'references/lifecycle.md', 'references/power-clock-reset.md',
            'references/bringup-debug.md', 'references/review-validation.md', 'references/evidence.md',
            'references/sources.md', 'assets/architecture-workbook.md', 'patterns/library.md',
            'examples/case-studies.md', 'examples/source-manifest.json', 'evals/prompts.json',
            'evals/rubric.md', 'evals/responses.md', 'evals/iteration-log.md',
            'evals/sizing-responses.md', 'scripts/sizing.py', 'examples/resource-camera.json',
            'examples/traffic-camera-sized.json', 'examples/traffic-camera-proposed.json']
for relative in required:
    if not (SKILL / relative).exists():
        errors.append(f'missing deliverable: {relative}')
print(json.dumps({'files_checked': len(files), 'entry_lines': len(entry.splitlines()), 'errors': errors}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
