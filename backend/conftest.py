"""
Pytest configuration for Meridian Ephemeris tests.
"""

import pytest

# Define custom markers to avoid warnings
pytest.mark.slow = pytest.mark.slow
pytest.mark.integration = pytest.mark.integration
pytest.mark.unit = pytest.mark.unit
pytest.mark.benchmark = pytest.mark.benchmark