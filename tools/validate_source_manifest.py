"""Validate the public evidence-role manifest; never ingest private source files."""
import json
from pathlib import Path


def validate(manifest):
    errors, seen = [], set()
    if not isinstance(manifest, dict) or set(manifest) != {'scope', 'sources'}:
        return ['manifest must contain only scope and sources']
    sources = manifest.get('sources')
    if not isinstance(sources, list) or not sources:
        return ['nonempty sources required']
    allowed = {'id', 'artifact_role', 'locator', 'evidence_scope'}
    for entry in sources:
        if not isinstance(entry, dict) or set(entry) != allowed:
            errors.append('source entry must contain only id/artifact_role/locator/evidence_scope')
            continue
        if not all(isinstance(v, str) and v.strip() for v in entry.values()):
            errors.append('source fields must be nonempty text')
            continue
        if entry['id'] in seen:
            errors.append('duplicate source id')
        seen.add(entry['id'])
    return errors


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'test-box-hardware-architecture/examples/source-manifest.json').read_text(encoding='utf-8'))
    errors = validate(data)
    print(json.dumps({'errors': errors}, indent=2))
    raise SystemExit(bool(errors))
