#!/usr/bin/env python
"""Performance measurement harness.

Measures cold and warm timings for key extracted subsystems:
  - aspects
  - arabic_parts (core + full traditional)
  - fixed_stars (subset)

Outputs JSON per run. Use --repeat N for statistical smoothing.
"""
from __future__ import annotations
import json, time, sys, statistics, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # ensure repo root importability


def measure_aspects():
    from extracted.systems.aspects import AspectCalculator  # type: ignore
    from extracted.systems.const import SwePlanets, normalize_longitude  # type: ignore
    from datetime import datetime, timezone
    import swisseph as swe  # type: ignore

    jd = swe.julday(2000,1,1,12.0)
    # Simple planet longitudes snapshot (Sun..Saturn)
    planet_ids = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]
    class _P:
        __slots__ = ("planet_id", "longitude", "longitude_speed")
        def __init__(self, planet_id: int, lon: float, speed: float):
            self.planet_id = planet_id
            self.longitude = lon
            self.longitude_speed = speed
    positions = []  # aspects calculator expects objects with planet_id, longitude, longitude_speed
    for pid in planet_ids:
        pos = swe.calc_ut(jd, pid)[0]  # (lon, lat, dist, lon_speed, ...)
        lon = normalize_longitude(pos[0])
        speed = pos[3] if len(pos) > 3 else 0.0
        positions.append(_P(pid, lon, speed))
    calc = AspectCalculator()
    return lambda: calc.calculate_aspects(positions)  # returns callable for timing


def measure_arabic_parts(full: bool):
    from extracted.systems.arabic_parts import ArabicPartsCalculator  # type: ignore
    from extracted.systems.arabic_parts_models import ArabicPartsRequest  # type: ignore
    from extracted.systems.classes.serialize import PlanetPosition, HouseSystem, ChartData  # type: ignore
    from extracted.systems.const import normalize_longitude  # type: ignore
    import swisseph as swe  # type: ignore
    from datetime import datetime, timezone

    jd = swe.julday(2000,1,1,12.0)
    # Provide classical + outer for consistent workload
    planet_ids = list(range(10))  # 0..9
    planets = {}
    for pid in planet_ids:
        vals = swe.calc_ut(jd, pid)[0]
        planets[pid] = PlanetPosition(planet_id=pid, longitude=vals[0], latitude=vals[1], distance=vals[2], longitude_speed=vals[3])
    # Equal house system starting at 0 Aries
    house_cusps = [i*30.0 for i in range(12)]
    ascmc = [0.0,90.0,180.0,270.0]
    houses = HouseSystem(house_cusps=house_cusps, ascmc=ascmc, system_code='P')
    chart = ChartData(planets=planets, houses=houses, julian_day=jd)
    calc = ArabicPartsCalculator()
    req = ArabicPartsRequest(include_all_traditional=full, include_optional_lots=full, requested_parts=['fortune'])
    return lambda: calc.calculate_arabic_parts(chart, req)


def measure_fixed_stars():
    from extracted.systems.fixed_stars import FixedStarCalculator  # type: ignore
    import swisseph as swe  # type: ignore
    jd = swe.julday(2000,1,1,12.0)
    calc = FixedStarCalculator()
    stars = ["Spica","Regulus","Aldebaran","Antares","Fomalhaut"]
    return lambda: calc.calculate_multiple_stars(stars, jd)


def time_callable(fn, warm_runs=3):
    # Cold
    start = time.perf_counter()
    fn()
    cold = (time.perf_counter() - start)*1000
    warms = []
    for _ in range(warm_runs):
        s = time.perf_counter(); fn(); warms.append((time.perf_counter()-s)*1000)
    return cold, warms


def summarize(name, fn):
    cold, warms = time_callable(fn)
    return {
        'name': name,
        'cold_ms': round(cold,3),
        'warm_ms_mean': round(statistics.mean(warms),3),
        'warm_ms_p95': round(sorted(warms)[int(len(warms)*0.95)-1],3) if warms else 0.0,
        'warm_runs': len(warms)
    }


def main():
    args = sys.argv[1:]
    targets = []
    if '--subsystem' in args:
        idx = args.index('--subsystem')
        if idx+1 < len(args):
            targets = [args[idx+1]]
    if not targets:
        targets = ['aspects','arabic_parts_core','arabic_parts_full','fixed_stars']

    results = []
    for t in targets:
        if t == 'aspects':
            results.append(summarize('aspects', measure_aspects()))
        elif t == 'arabic_parts_core':
            results.append(summarize('arabic_parts_core', measure_arabic_parts(full=False)))
        elif t == 'arabic_parts_full':
            results.append(summarize('arabic_parts_full', measure_arabic_parts(full=True)))
        elif t == 'fixed_stars':
            results.append(summarize('fixed_stars', measure_fixed_stars()))
    print(json.dumps({'perf': results}, indent=2))

if __name__ == '__main__':
    main()
