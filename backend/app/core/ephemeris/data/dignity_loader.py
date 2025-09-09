"""
Essential Dignities Reference Data Loader
Loads authoritative dignity data from reference files following project standards.
"""

import json
import csv
import os
from typing import Dict, Any, Optional
from functools import lru_cache
from pathlib import Path


class DignityDataLoader:
    """Load and validate essential dignities reference data."""
    
    def __init__(self):
        # Path from backend/app/core/ephemeris/data/ to PRPS CONSTRUCTION MAGIC/
        self._base_path = Path(__file__).parent.parent.parent.parent.parent / "PRPS CONSTRUCTION MAGIC" / "BUILD RESOURCES" / "Astrological Reference"
        # Verify path exists, if not try alternative path
        if not self._base_path.exists():
            # Try direct path from project root
            project_root = Path(__file__).parent
            while project_root.name != "ASTRO MERIDIAN APP V1.0" and project_root.parent != project_root:
                project_root = project_root.parent
            self._base_path = project_root / "PRPS CONSTRUCTION MAGIC" / "BUILD RESOURCES" / "Astrological Reference"
        
        self._data_cache: Dict[str, Any] = {}
    
    @lru_cache(maxsize=1)
    def load_essential_dignities_database(self) -> Dict[str, Any]:
        """Load the main essential dignities database JSON with fallback."""
        file_path = self._base_path / "essential_dignities_database.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._validate_database_structure(data)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to hardcoded data if file not found or invalid
            return self._get_fallback_dignity_data()
    
    def _get_fallback_dignity_data(self) -> Dict[str, Any]:
        """
        Get fallback essential dignities data when files are unavailable.
        
        RULERSHIP POLICY: This system uses traditional rulerships only.
        - Mars rules Aries and Scorpio (traditional)
        - Saturn rules Capricorn and Aquarius (traditional)  
        - Jupiter rules Sagittarius and Pisces (traditional)
        
        Modern rulerships (Uranus/Aquarius, Neptune/Pisces, Pluto/Scorpio) 
        are NOT used for essential dignities calculations, following 
        traditional astrological practice as outlined in William Lilly's work.
        """
        return {
            "metadata": {
                "version": "1.0",
                "sources_note": "Fallback traditional dignity data",
                "triplicity_scheme": "Dorothean (day/night/participating)",
                "bounds_system": "egyptian",
                "bounds_source": "Egyptian/Dorothean terms as used by William Lilly"
            },
            "planets": {
                "Sun": {
                    "domiciles": ["Leo"],
                    "detriments": ["Aquarius"],
                    "exaltation": {"sign": "Aries", "degree": 19},
                    "fall": {"sign": "Libra", "degree": 19}
                },
                "Moon": {
                    "domiciles": ["Cancer"],
                    "detriments": ["Capricorn"],
                    "exaltation": {"sign": "Taurus", "degree": 3},
                    "fall": {"sign": "Scorpio", "degree": 3}
                },
                "Mercury": {
                    "domiciles": ["Gemini", "Virgo"],
                    "detriments": ["Sagittarius", "Pisces"],
                    "exaltation": {"sign": "Virgo", "degree": 15},
                    "fall": {"sign": "Pisces", "degree": 15}
                },
                "Venus": {
                    "domiciles": ["Taurus", "Libra"],
                    "detriments": ["Scorpio", "Aries"],
                    "exaltation": {"sign": "Pisces", "degree": 27},
                    "fall": {"sign": "Virgo", "degree": 27}
                },
                "Mars": {
                    "domiciles": ["Aries", "Scorpio"],
                    "detriments": ["Libra", "Taurus"],
                    "exaltation": {"sign": "Capricorn", "degree": 28},
                    "fall": {"sign": "Cancer", "degree": 28}
                },
                "Jupiter": {
                    "domiciles": ["Sagittarius", "Pisces"],
                    "detriments": ["Gemini", "Virgo"],
                    "exaltation": {"sign": "Cancer", "degree": 15},
                    "fall": {"sign": "Capricorn", "degree": 15}
                },
                "Saturn": {
                    "domiciles": ["Capricorn", "Aquarius"],
                    "detriments": ["Cancer", "Leo"],
                    "exaltation": {"sign": "Libra", "degree": 21},
                    "fall": {"sign": "Aries", "degree": 21}
                }
            },
            "triplicities": {
                "Fire": {"day_ruler": "Sun", "night_ruler": "Jupiter", "participating_ruler": "Saturn"},
                "Earth": {"day_ruler": "Venus", "night_ruler": "Moon", "participating_ruler": "Mars"},
                "Air": {"day_ruler": "Saturn", "night_ruler": "Mercury", "participating_ruler": "Jupiter"},
                "Water": {"day_ruler": "Venus", "night_ruler": "Mars", "participating_ruler": "Moon"}
            },
            "bounds_egyptian": self._get_fallback_bounds(),
            "decans_chaldean": self._get_fallback_decans()
        }
    
    def _get_fallback_bounds(self) -> Dict[str, list]:
        """Fallback Egyptian bounds data."""
        return {
            "Aries": [
                {"start_deg": 0, "end_deg": 6, "ruler": "Jupiter"},
                {"start_deg": 6, "end_deg": 14, "ruler": "Venus"},
                {"start_deg": 14, "end_deg": 21, "ruler": "Mercury"},
                {"start_deg": 21, "end_deg": 26, "ruler": "Mars"},
                {"start_deg": 26, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Taurus": [
                {"start_deg": 0, "end_deg": 8, "ruler": "Venus"},
                {"start_deg": 8, "end_deg": 14, "ruler": "Mercury"},
                {"start_deg": 14, "end_deg": 22, "ruler": "Jupiter"},
                {"start_deg": 22, "end_deg": 27, "ruler": "Saturn"},
                {"start_deg": 27, "end_deg": 30, "ruler": "Mars"}
            ],
            "Gemini": [
                {"start_deg": 0, "end_deg": 6, "ruler": "Jupiter"},
                {"start_deg": 6, "end_deg": 14, "ruler": "Venus"},
                {"start_deg": 14, "end_deg": 21, "ruler": "Mercury"},
                {"start_deg": 21, "end_deg": 28, "ruler": "Mars"},
                {"start_deg": 28, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Cancer": [
                {"start_deg": 0, "end_deg": 7, "ruler": "Mars"},
                {"start_deg": 7, "end_deg": 13, "ruler": "Venus"},
                {"start_deg": 13, "end_deg": 19, "ruler": "Mercury"},
                {"start_deg": 19, "end_deg": 28, "ruler": "Jupiter"},
                {"start_deg": 28, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Leo": [
                {"start_deg": 0, "end_deg": 6, "ruler": "Saturn"},
                {"start_deg": 6, "end_deg": 13, "ruler": "Mercury"},
                {"start_deg": 13, "end_deg": 19, "ruler": "Venus"},
                {"start_deg": 19, "end_deg": 25, "ruler": "Jupiter"},
                {"start_deg": 25, "end_deg": 30, "ruler": "Mars"}
            ],
            "Virgo": [
                {"start_deg": 0, "end_deg": 7, "ruler": "Mercury"},
                {"start_deg": 7, "end_deg": 13, "ruler": "Venus"},
                {"start_deg": 13, "end_deg": 17, "ruler": "Jupiter"},
                {"start_deg": 17, "end_deg": 21, "ruler": "Mercury"},
                {"start_deg": 21, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Libra": [
                {"start_deg": 0, "end_deg": 6, "ruler": "Saturn"},
                {"start_deg": 6, "end_deg": 14, "ruler": "Mercury"},
                {"start_deg": 14, "end_deg": 21, "ruler": "Jupiter"},
                {"start_deg": 21, "end_deg": 28, "ruler": "Venus"},
                {"start_deg": 28, "end_deg": 30, "ruler": "Mars"}
            ],
            "Scorpio": [
                {"start_deg": 0, "end_deg": 7, "ruler": "Mars"},
                {"start_deg": 7, "end_deg": 13, "ruler": "Venus"},
                {"start_deg": 13, "end_deg": 19, "ruler": "Mercury"},
                {"start_deg": 19, "end_deg": 24, "ruler": "Jupiter"},
                {"start_deg": 24, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Sagittarius": [
                {"start_deg": 0, "end_deg": 12, "ruler": "Jupiter"},
                {"start_deg": 12, "end_deg": 17, "ruler": "Venus"},
                {"start_deg": 17, "end_deg": 21, "ruler": "Mercury"},
                {"start_deg": 21, "end_deg": 26, "ruler": "Saturn"},
                {"start_deg": 26, "end_deg": 30, "ruler": "Mars"}
            ],
            "Capricorn": [
                {"start_deg": 0, "end_deg": 7, "ruler": "Mercury"},
                {"start_deg": 7, "end_deg": 14, "ruler": "Jupiter"},
                {"start_deg": 14, "end_deg": 22, "ruler": "Venus"},
                {"start_deg": 22, "end_deg": 26, "ruler": "Saturn"},
                {"start_deg": 26, "end_deg": 30, "ruler": "Mars"}
            ],
            "Aquarius": [
                {"start_deg": 0, "end_deg": 7, "ruler": "Mercury"},
                {"start_deg": 7, "end_deg": 13, "ruler": "Venus"},
                {"start_deg": 13, "end_deg": 20, "ruler": "Jupiter"},
                {"start_deg": 20, "end_deg": 25, "ruler": "Mars"},
                {"start_deg": 25, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Pisces": [
                {"start_deg": 0, "end_deg": 12, "ruler": "Venus"},
                {"start_deg": 12, "end_deg": 19, "ruler": "Jupiter"},
                {"start_deg": 19, "end_deg": 24, "ruler": "Mercury"},
                {"start_deg": 24, "end_deg": 27, "ruler": "Mars"},
                {"start_deg": 27, "end_deg": 30, "ruler": "Saturn"}
            ]
        }
    
    def _get_fallback_decans(self) -> Dict[str, list]:
        """Fallback Chaldean decans data."""
        return {
            "Aries": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Mars"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Sun"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Venus"}
            ],
            "Taurus": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Mercury"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Moon"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Gemini": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Jupiter"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Mars"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Sun"}
            ],
            "Cancer": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Venus"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Mercury"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Moon"}
            ],
            "Leo": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Saturn"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Jupiter"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Mars"}
            ],
            "Virgo": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Sun"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Venus"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Mercury"}
            ],
            "Libra": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Moon"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Saturn"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Jupiter"}
            ],
            "Scorpio": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Mars"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Sun"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Venus"}
            ],
            "Sagittarius": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Mercury"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Moon"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Saturn"}
            ],
            "Capricorn": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Jupiter"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Mars"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Sun"}
            ],
            "Aquarius": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Venus"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Mercury"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Moon"}
            ],
            "Pisces": [
                {"start_deg": 0, "end_deg": 10, "ruler": "Saturn"},
                {"start_deg": 10, "end_deg": 20, "ruler": "Jupiter"},
                {"start_deg": 20, "end_deg": 30, "ruler": "Mars"}
            ]
        }
    
    @lru_cache(maxsize=1)
    def load_triplicity_rulers(self) -> Dict[str, Dict[str, str]]:
        """Load Dorothean triplicity rulers from CSV."""
        file_path = self._base_path / "triplicity_rulers_dorothean.csv"
        
        try:
            triplicities = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    element = row['element'].lower()
                    triplicities[element] = {
                        'day_ruler': row['day_ruler'],
                        'night_ruler': row['night_ruler'],
                        'participating_ruler': row['participating_ruler']
                    }
            return triplicities
        except FileNotFoundError:
            raise FileNotFoundError(f"Triplicity rulers file not found at {file_path}")
    
    @lru_cache(maxsize=1)
    def load_bounds_egyptian(self) -> Dict[str, list]:
        """Load Egyptian bounds/terms from CSV."""
        file_path = self._base_path / "bounds_egyptian.csv"
        
        try:
            bounds = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sign = row['sign']
                    if sign not in bounds:
                        bounds[sign] = []
                    
                    bounds[sign].append({
                        'start_deg': float(row['start_deg']),
                        'end_deg': float(row['end_deg']),
                        'ruler': row['ruler']
                    })
            return bounds
        except FileNotFoundError:
            raise FileNotFoundError(f"Egyptian bounds file not found at {file_path}")
    
    @lru_cache(maxsize=1)
    def load_decans_chaldean(self) -> Dict[str, list]:
        """Load Chaldean decans/faces from CSV."""
        file_path = self._base_path / "decans_chaldean.csv"
        
        try:
            decans = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sign = row['sign']
                    if sign not in decans:
                        decans[sign] = []
                    
                    decans[sign].append({
                        'start_deg': float(row['start_deg']),
                        'end_deg': float(row['end_deg']),
                        'ruler': row['ruler']
                    })
            return decans
        except FileNotFoundError:
            raise FileNotFoundError(f"Chaldean decans file not found at {file_path}")
    
    def get_planet_dignities(self, planet_name: str) -> Dict[str, Any]:
        """Get all dignity data for a specific planet."""
        db = self.load_essential_dignities_database()
        return db['planets'].get(planet_name, {})
    
    def get_sign_element(self, sign_name: str) -> Optional[str]:
        """Get the element for a zodiac sign."""
        sign_elements = {
            'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
            'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
            'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
            'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
        }
        return sign_elements.get(sign_name)
    
    def get_triplicity_ruler(self, element: str, sect: str) -> Optional[str]:
        """Get triplicity ruler for element and sect (day/night)."""
        triplicities = self.load_triplicity_rulers()
        element_data = triplicities.get(element.lower(), {})
        
        if sect == 'day':
            return element_data.get('day_ruler')
        elif sect == 'night':
            return element_data.get('night_ruler')
        elif sect == 'participating':
            return element_data.get('participating_ruler')
        
        return None
    
    def get_bound_ruler(self, sign_name: str, degree: float) -> Optional[str]:
        """Get Egyptian bounds ruler for sign and degree."""
        try:
            bounds = self.load_bounds_egyptian()
        except FileNotFoundError:
            # Use fallback data
            dignity_data = self._get_fallback_dignity_data()
            bounds = dignity_data.get('bounds_egyptian', {})
        
        sign_bounds = bounds.get(sign_name, [])
        
        for bound in sign_bounds:
            if bound['start_deg'] <= degree < bound['end_deg']:
                return bound['ruler']
        
        return None
    
    def get_face_ruler(self, sign_name: str, degree: float) -> Optional[str]:
        """Get Chaldean face/decan ruler for sign and degree."""
        faces = self.load_decans_chaldean()
        sign_faces = faces.get(sign_name, [])
        
        for face in sign_faces:
            if face['start_deg'] <= degree < face['end_deg']:
                return face['ruler']
        
        return None
    
    def _validate_database_structure(self, data: Dict[str, Any]) -> None:
        """Validate the essential dignities database structure."""
        required_keys = ['metadata', 'planets', 'triplicities', 'decans_chaldean', 'bounds_egyptian']
        
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key '{key}' in dignities database")
        
        # Validate planets section
        if not isinstance(data['planets'], dict):
            raise ValueError("'planets' section must be a dictionary")
        
        # Check for required planets
        required_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for planet in required_planets:
            if planet not in data['planets']:
                raise ValueError(f"Missing required planet '{planet}' in database")


# Global instance for caching
_dignity_loader: Optional[DignityDataLoader] = None

def get_dignity_loader() -> DignityDataLoader:
    """Get singleton dignity data loader instance."""
    global _dignity_loader
    if _dignity_loader is None:
        _dignity_loader = DignityDataLoader()
    return _dignity_loader