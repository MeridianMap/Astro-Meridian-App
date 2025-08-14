"""
Meridian Ephemeris ACG (Astrocartography) Module

This module provides comprehensive astrocartography calculations for natal charts,
implementing all major line types (MC, IC, AC, DC, aspects, parans) and supporting
all celestial bodies (planets, asteroids, fixed stars, hermetic lots, lunar nodes).

Features:
- Complete line type calculations (MC, IC, AC, DC, aspects to AC/MC, parans)
- All supported celestial bodies (planets, asteroids, hermetic lots, fixed stars, nodes)
- High-performance calculations with caching and batch processing
- GeoJSON output with full metadata and provenance
- Integration with natal chart data for complete astrological context
- Swiss Ephemeris-based calculations for accuracy

Modules:
- acg_types: Data models and type definitions
- acg_core: Core calculation engine
- acg_metadata: Metadata and provenance handling
- acg_cache: Caching and optimization layer
- acg_utils: Utility functions and helpers
"""

from .acg_types import (
    ACGResult,
    ACGRequest,
    ACGBodyData,
    ACGLineData,
    ACGMetadata,
    ACGNatalData,
    ACGOptions
)

__all__ = [
    'ACGResult',
    'ACGRequest', 
    'ACGBodyData',
    'ACGLineData',
    'ACGMetadata',
    'ACGNatalData',
    'ACGOptions'
]

__version__ = '1.0.0'