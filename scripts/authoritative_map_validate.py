#!/usr/bin/env python
"""Validate authoritative_map.json importability.

Loads each legacy -> extracted mapping, attempts imports, and reports JSON status.
Exit code 1 if any mapping fails.
"""
from __future__ import annotations
import json, importlib, sys, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / 'extracted' / 'authoritative_map.json'


def try_import(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def main():
    if not MAP_PATH.exists():
        print(json.dumps({'error': 'authoritative_map_missing', 'path': str(MAP_PATH)}))
        sys.exit(1)
    data = json.loads(MAP_PATH.read_text())
    results = []
    failures = 0
    for legacy, extracted in data.items():
        start = time.perf_counter()
        legacy_ok = try_import(legacy)
        legacy_time = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        extracted_ok = try_import(extracted)
        extracted_time = (time.perf_counter() - start) * 1000
        ok = legacy_ok and extracted_ok
        if not ok:
            failures += 1
        results.append({
            'legacy': legacy,
            'extracted': extracted,
            'legacy_import_ok': legacy_ok,
            'extracted_import_ok': extracted_ok,
            'legacy_import_ms': round(legacy_time, 2),
            'extracted_import_ms': round(extracted_time, 2),
            'ok': ok,
        })
    payload = {'results': results, 'failures': failures}
    print(json.dumps(payload, indent=2))
    sys.exit(1 if failures else 0)

if __name__ == '__main__':
    main()
