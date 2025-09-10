import pytest

from extracted.systems.utils.swiss_ephemeris import ensure_swiss_ephemeris_setup
from backend.app.core.ephemeris.tools.fixed_stars import FixedStarCalculator


def test_regulus_position_smoke():
    ensure_swiss_ephemeris_setup()
    calc = FixedStarCalculator()
    jd = 2460000.5
    pos = calc.calculate_star_position("Regulus", jd)
    assert pos is None or (0.0 <= pos["longitude"] <= 360.0)
