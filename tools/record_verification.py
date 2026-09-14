"""Run bounded offline checks and preserve actual outputs for release review."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'test-box-hardware-architecture'
checks = [
    ('package', [sys.executable, '-X', 'utf8', str(ROOT / 'tools/check_package.py')], 0),
    ('unit-tests', [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', str(P / 'evals'), '-p', 'test_*.py', '-v'], 0),
]
for command, filename, extra, expected in [
    ('diff', 'lifecycle-demo.json', ['--before', 'DUT_OFF', '--after', 'ACTIVE'], 1),
    ('dependency', 'dependency-demo.json', ['--changed', 'SERDES'], 0),
    ('budget', 'budget-demo.json', [], 1), ('trace', 'trace-demo.json', [], 1),
    ('budget', 'traffic-camera-proposed.json', [], 1),
    ('budget', 'traffic-camera-sized.json', [], 0),
    ('resource', 'resource-camera.json', ['--traffic', str(P / 'examples/traffic-camera-proposed.json')], 1),
    ('resource', 'resource-camera.json', ['--traffic', str(P / 'examples/traffic-camera-sized.json')], 0)
]:
    checks.append((command, [sys.executable, '-X', 'utf8', str(P / 'scripts/arch_tools.py'), command, str(P / 'examples' / filename), *extra], expected))
results = []
for name, command, expected in checks:
    run = subprocess.run(command, cwd=ROOT, capture_output=True, encoding='utf-8', timeout=60)
    results.append(dict(name=name, input=Path(command[5]).name if len(command) > 5 and command[3].endswith('arch_tools.py') else None,
                        expected_exit=expected, exit_code=run.returncode,
                        passed=run.returncode == expected, stdout=run.stdout, stderr=run.stderr))
target = ROOT / 'reports/verification.json'
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),
                                scope='Offline structural and algorithm checks; not behavioral or hardware approval',
                                checks=results), ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'checks': len(results), 'passed': sum(r['passed'] for r in results), 'report': str(target)}))
raise SystemExit(not all(r['passed'] for r in results))
