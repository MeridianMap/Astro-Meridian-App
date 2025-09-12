#!/usr/bin/env python
"""Generate/update performance baseline JSON.
Writes to perf_baseline.json at repo root.
"""
from __future__ import annotations
import json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / 'perf_baseline.json'


def run_measure():
    cmd = [sys.executable, str(ROOT / 'scripts' / 'measure_perf.py')]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def main():
    data = run_measure()
    data['baseline_version'] = 1
    BASELINE_PATH.write_text(json.dumps(data, indent=2))
    print(f"Wrote baseline to {BASELINE_PATH}")

if __name__ == '__main__':
    main()
