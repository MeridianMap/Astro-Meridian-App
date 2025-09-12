#!/usr/bin/env python
"""
Compare current perf JSON against baseline and exit nonzero if regressions exceed thresholds.
Usage:
  python scripts/compare_perf_to_baseline.py perf_baseline.json perf_current.json --abs-ms 10 --rel 3.0
Meaning:
  --abs-ms: allowed absolute increase in warm_ms_mean in milliseconds
  --rel: allowed multiplicative increase (e.g., 2.0 means up to 2x baseline)
"""
from __future__ import annotations
import json, sys

def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    if len(sys.argv) < 3:
        print("Usage: compare_perf_to_baseline.py <baseline.json> <current.json> [--abs-ms N] [--rel X]", file=sys.stderr)
        return 2
    baseline_path, current_path = sys.argv[1], sys.argv[2]
    abs_ms = 10.0
    rel = 3.0
    if '--abs-ms' in sys.argv:
        try:
            abs_ms = float(sys.argv[sys.argv.index('--abs-ms')+1])
        except Exception:
            pass
    if '--rel' in sys.argv:
        try:
            rel = float(sys.argv[sys.argv.index('--rel')+1])
        except Exception:
            pass

    base = load(baseline_path)
    curr = load(current_path)

    # Map name -> warm_ms_mean
    base_map = {x['name']: x['warm_ms_mean'] for x in base.get('perf', [])}
    curr_map = {x['name']: x['warm_ms_mean'] for x in curr.get('perf', [])}

    failures = []
    for name, base_mean in base_map.items():
        cur_mean = curr_map.get(name)
        if cur_mean is None:
            continue
        if cur_mean - base_mean > abs_ms and (cur_mean / max(base_mean, 0.0001)) > rel:
            failures.append((name, base_mean, cur_mean))

    if failures:
        print("Perf regressions detected (name, baseline, current):", file=sys.stderr)
        for name, b, c in failures:
            print(f"  - {name}: {b} -> {c} ms", file=sys.stderr)
        return 1
    print("Perf within thresholds.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
