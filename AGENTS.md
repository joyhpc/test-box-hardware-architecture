# Maintenance contract

The maintained package is `test-box-hardware-architecture/`. Keep the entry point short and place conditional domain detail in linked references.

- Preserve the top-down chain, module contracts, partial-power states, state transitions, and evidence/version distinctions.
- Local project examples are scoped evidence, never universal architecture requirements. Do not modify historical hardware source projects during skill maintenance.
- Keep offline scripts standard-library-only and unable to operate hardware. Do not replace engineering judgments with lexical checklist scores.
- Run `python -X utf8 tools/check_package.py` and `python -X utf8 -m unittest discover -s test-box-hardware-architecture/evals -p 'test_*.py' -v` after relevant changes.
- Retain actual behavioral responses, evaluator identity, limitations, failures and retests. Do not label author self-review as independent evaluation.
- Do not silently overwrite an existing installed skill. Maintain this workspace as the source and record installation fingerprints separately.
