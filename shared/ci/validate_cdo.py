#!/usr/bin/env python3
"""CDO JSON schema validator — all config JSONs must have _meta field.

Usage: python3 validate_cdo.py [directory] [--strict]
  directory: scan target (default: current directory)
  --strict: fail on missing _meta (default: warn only)

Exit codes: 0=pass, 1=violations found
"""
import json
import os
import sys

SKIP_DIRS = {'.git', 'node_modules', 'target', '__pycache__', '.local', 'venv', '.venv'}
SKIP_FILES = {'package.json', 'package-lock.json', 'tsconfig.json',
              'Cargo.lock', '.claude/settings.local.json'}


def scan_jsons(directory):
    results = {'ok': [], 'warn': [], 'fail': []}
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if not f.endswith('.json'):
                continue
            rel = os.path.relpath(os.path.join(root, f), directory)
            if any(rel.endswith(s) for s in SKIP_FILES):
                continue
            if '.claude/' in rel:
                continue
            path = os.path.join(root, f)
            if os.path.islink(path) and not os.path.exists(path):
                continue  # skip broken symlinks
            try:
                with open(path) as fh:
                    data = json.load(fh)
            except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
                results['fail'].append((rel, f'parse error: {e}'))
                continue
            if not isinstance(data, dict):
                continue  # arrays etc. are not config JSONs
            if '_meta' in data:
                meta = data['_meta']
                missing = [k for k in ('description', 'updated', 'schema_version')
                           if k not in meta]
                if missing:
                    results['warn'].append((rel, f'_meta missing fields: {missing}'))
                else:
                    results['ok'].append(rel)
            else:
                results['warn'].append((rel, 'no _meta field'))
    return results


def main():
    directory = '.'
    strict = False
    for arg in sys.argv[1:]:
        if arg == '--strict':
            strict = True
        else:
            directory = arg

    results = scan_jsons(directory)
    total = len(results['ok']) + len(results['warn']) + len(results['fail'])

    print(f"CDO JSON Validation: {directory}")
    print(f"  OK: {len(results['ok'])}  Warn: {len(results['warn'])}  Fail: {len(results['fail'])}  Total: {total}")

    if results['ok']:
        print("\n[OK] CDO compliant:")
        for f in results['ok']:
            print(f"  {f}")

    if results['warn']:
        print("\n[WARN] Missing CDO structure:")
        for f, msg in results['warn']:
            print(f"  {f}: {msg}")

    if results['fail']:
        print("\n[FAIL] Broken JSON:")
        for f, msg in results['fail']:
            print(f"  {f}: {msg}")

    convergence = len(results['ok']) / total * 100 if total > 0 else 100
    print(f"\nConvergence: {convergence:.0f}% ({len(results['ok'])}/{total})")

    if results['fail']:
        sys.exit(1)
    if strict and results['warn']:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
