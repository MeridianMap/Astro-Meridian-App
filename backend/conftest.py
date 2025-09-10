"""
Pytest configuration for Meridian Ephemeris tests.
Ensures repository root is on sys.path so the extracted/ package is importable.
"""

import os
import sys
from pathlib import Path
import pytest

# Ensure repo root (parent of backend/) is importable for 'extracted' package
_here = Path(__file__).resolve()
_repo_root = _here.parents[1]
if str(_repo_root) not in sys.path:
	sys.path.insert(0, str(_repo_root))

# Define custom markers to avoid warnings
pytest.mark.slow = pytest.mark.slow
pytest.mark.integration = pytest.mark.integration
pytest.mark.unit = pytest.mark.unit
pytest.mark.benchmark = pytest.mark.benchmark