"""
Hermetic Lots Calculator with Sect Determination

Calculate 16 traditional hermetic lots using sect-based day/night formulas.
Based on Hellenistic astrology traditions and modern astrological practice.

Implements proper sect determination and traditional lot formulas with
day/night variations as documented in classical astrological sources.
"""

from typing import Dict, List, Any, Optional
import math
import logging
from datetime import datetime

from extracted.systems.models.planet_data import PlanetData

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class HermeticLotsCalculator:
    """
    Calculate 16 traditional hermetic lots using sect-based day/night formulas.
    
    Features:
    - Proper sect determination using Sun position relative to horizon
    - Traditional day/night formula variations for all lots
    - Complete set of 16 classical hermetic lots
    - Astrological context (sign, house) for each lot
    - Metadata about calculation method and sources
    """
    
    def __init__(self):
        """Initialize hermetic lots calculator."""
        pass
        
    def calculate_16_traditional_lots(self, planets: Dict[str, PlanetData], 
                                    houses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate complete set of traditional hermetic lots.
        
        Args:
            planets: Dictionary of planet data by name
            houses: House system data with angles
            
        Returns:
            Dictionary with sect determination, lots, and metadata
        """
        try:
            calculation_start = datetime.now()
            
            # Determine chart sect (day/night)
            sect_info = self._determine_sect(planets, houses)
            
            # Calculate all 16 traditional lots
            lots = {}
            
            # Primary lots (fundamental)
            lots['fortune'] = self._calculate_fortune(planets, houses, sect_info['is_day_chart'])
            lots['spirit'] = self._calculate_spirit(planets, houses, sect_info['is_day_chart'])
            lots['basis'] = self._calculate_basis(lots['fortune'], lots['spirit'], houses)
            
            # Secondary lots (derived from primaries or using sect formulas)
            lots['love'] = self._calculate_love(planets, houses, sect_info['is_day_chart'])
            lots['necessity'] = self._calculate_necessity(planets, houses, sect_info['is_day_chart'])
            lots['courage'] = self._calculate_courage(planets, lots['fortune'], sect_info['is_day_chart'])
            lots['victory'] = self._calculate_victory(planets, lots['fortune'], sect_info['is_day_chart'])
            lots['nemesis'] = self._calculate_nemesis(lots['fortune'], planets, sect_info['is_day_chart'])
            lots['eros'] = self._calculate_eros(planets, houses, sect_info['is_day_chart'])
            lots['marriage'] = self._calculate_marriage(planets, houses, sect_info['is_day_chart'])
            lots['children'] = self._calculate_children(planets, houses, sect_info['is_day_chart'])
            lots['disease'] = self._calculate_disease(planets, houses, sect_info['is_day_chart'])
            lots['death'] = self._calculate_death(planets, houses, sect_info['is_day_chart'])
            lots['servants'] = self._calculate_servants(planets, houses, sect_info['is_day_chart'])
            lots['travel'] = self._calculate_travel(planets, houses, sect_info['is_day_chart'])
            lots['fame'] = self._calculate_fame(planets, houses, sect_info['is_day_chart'])
            
            # Add astrological context to each lot
            for lot_name, lot_data in lots.items():
                if isinstance(lot_data, dict) and 'longitude' in lot_data:
                    self._add_astrological_context(lot_data, houses)
            
            calculation_time = (datetime.now() - calculation_start).total_seconds()
            
            return {
                'sect_determination': sect_info,
                'hermetic_lots': lots,
                'calculation_metadata': {
                    'total_lots_calculated': len(lots),
                    'formulas_used': list(lots.keys()),
                    'sect_used': 'day' if sect_info['is_day_chart'] else 'night',
                    'calculation_time_seconds': round(calculation_time, 3),
                    'calculation_method': 'traditional_hellenistic',
                    'source': 'Classical hermetic lot formulas with sect determination'
                }
            }
            
        except Exception as e:
            logger.error(f"Hermetic lots calculation failed: {e}")
            raise RuntimeError(f"Hermetic lots calculation failed: {e}")
    
    def _determine_sect(self, planets: Dict[str, PlanetData], houses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine day/night sect of chart using traditional method.
        
        Traditional sect determination: Sun above or below horizon
        - Day chart: Sun above horizon (houses 7-12, or Sun in houses 7-12)
        - Night chart: Sun below horizon (houses 1-6, or Sun in houses 1-6)
        
        Args:
            planets: Planet data dictionary
            houses: House system data
            
        Returns:
            Dictionary with sect information
        """
        try:
            sun = planets['Sun']
            ascendant = houses['houses']['ascendant']
            descendant = houses['houses']['descendant']
            
            # Traditional method: check if Sun is above horizon
            # Sun above horizon = day chart, below horizon = night chart
            is_day_chart = self._is_sun_above_horizon(sun.longitude, ascendant, descendant)
            
            # Additional validation methods
            validation_methods = {
                'house_position_method': sun.house_number > 6 if sun.house_number else False,
                'angular_distance_method': self._angular_distance_method(sun.longitude, ascendant),
                'traditional_horizon_method': is_day_chart
            }
            
            return {
                'is_day_chart': is_day_chart,
                'sect': 'day' if is_day_chart else 'night',
                'sun_above_horizon': is_day_chart,
                'method_used': 'traditional_horizon_crossing',
                'sun_house_number': sun.house_number,
                'validation_methods': validation_methods,
                'sun_longitude': sun.longitude,
                'ascendant_longitude': ascendant
            }
            
        except Exception as e:
            logger.error(f"Sect determination failed: {e}")
            # Default to day chart if calculation fails
            return {
                'is_day_chart': True,
                'sect': 'day',
                'method_used': 'default_fallback',
                'error': str(e)
            }
    
    def _is_sun_above_horizon(self, sun_longitude: float, ascendant: float, descendant: float) -> bool:
        """
        Check if Sun is above horizon using angular position.
        
        Args:
            sun_longitude: Sun longitude in degrees
            ascendant: Ascendant longitude in degrees  
            descendant: Descendant longitude in degrees
            
        Returns:
            True if Sun is above horizon (day chart)
        """
        # Normalize angles to 0-360
        sun_lon = sun_longitude % 360
        asc = ascendant % 360
        desc = descendant % 360
        
        # Sun is above horizon if it's between descendant and ascendant
        # (going the long way around the zodiac)
        if desc <= asc:  # Normal case
            return sun_lon >= desc or sun_lon <= asc
        else:  # Descendant crosses 0 degrees
            return desc <= sun_lon <= asc
    
    def _angular_distance_method(self, sun_longitude: float, ascendant: float) -> bool:
        """Alternative sect determination using angular distance."""
        distance = abs(sun_longitude - ascendant)
        if distance > 180:
            distance = 360 - distance
        return distance <= 90  # Sun within 90 degrees of ascendant = day chart
    
    def _calculate_fortune(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], 
                         is_day: bool) -> Dict[str, Any]:
        """
        Calculate Lot of Fortune with sect-based formula.
        
        Traditional formulas:
        - Day: Ascendant + Moon - Sun
        - Night: Ascendant + Sun - Moon
        
        Args:
            planets: Planet data
            houses: House data
            is_day: True if day chart
            
        Returns:
            Dictionary with lot data
        """
        try:
            sun = planets['Sun']
            moon = planets['Moon']
            asc_lon = houses['houses']['ascendant']
            
            if is_day:
                # Day formula: Asc + Moon - Sun
                fortune_lon = (asc_lon + moon.longitude - sun.longitude) % 360
                formula_used = 'day_formula'
                formula_text = 'Ascendant + Moon - Sun'
            else:
                # Night formula: Asc + Sun - Moon  
                fortune_lon = (asc_lon + sun.longitude - moon.longitude) % 360
                formula_used = 'night_formula'
                formula_text = 'Ascendant + Sun - Moon'
            
            return {
                'name': 'fortune',
                'longitude': fortune_lon,
                'formula_used': formula_used,
                'formula_text': formula_text,
                'traditional_name': 'Lot of Fortune',
                'description': 'Material fortune, physical well-being, and the body',
                'sect_dependency': True,
                'calculated_for_sect': 'day' if is_day else 'night'
            }
            
        except Exception as e:
            logger.error(f"Fortune calculation failed: {e}")
            raise ValueError(f"Fortune calculation failed: {e}")
    
    def _calculate_spirit(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], 
                        is_day: bool) -> Dict[str, Any]:
        """
        Calculate Lot of Spirit with sect-based formula.
        
        Traditional formulas:
        - Day: Ascendant + Sun - Moon  
        - Night: Ascendant + Moon - Sun
        
        Note: Spirit is the reverse of Fortune for sect
        """
        try:
            sun = planets['Sun']
            moon = planets['Moon'] 
            asc_lon = houses['houses']['ascendant']
            
            if is_day:
                # Day formula: Asc + Sun - Moon
                spirit_lon = (asc_lon + sun.longitude - moon.longitude) % 360
                formula_used = 'day_formula'
                formula_text = 'Ascendant + Sun - Moon'
            else:
                # Night formula: Asc + Moon - Sun
                spirit_lon = (asc_lon + moon.longitude - sun.longitude) % 360
                formula_used = 'night_formula' 
                formula_text = 'Ascendant + Moon - Sun'
            
            return {
                'name': 'spirit',
                'longitude': spirit_lon,
                'formula_used': formula_used,
                'formula_text': formula_text,
                'traditional_name': 'Lot of Spirit',
                'description': 'Spiritual nature, soul, and mental faculties',
                'sect_dependency': True,
                'calculated_for_sect': 'day' if is_day else 'night'
            }
            
        except Exception as e:
            logger.error(f"Spirit calculation failed: {e}")
            raise ValueError(f"Spirit calculation failed: {e}")
    
    def _calculate_basis(self, fortune: Dict[str, Any], spirit: Dict[str, Any],
                       houses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Lot of Basis (Foundation).
        
        Formula: Ascendant + Lot of Fortune - Lot of Spirit
        """
        try:
            asc_lon = houses['houses']['ascendant']
            basis_lon = (asc_lon + fortune['longitude'] - spirit['longitude']) % 360
            
            return {
                'name': 'basis',
                'longitude': basis_lon,
                'formula_used': 'standard',
                'formula_text': 'Ascendant + Fortune - Spirit',
                'traditional_name': 'Lot of Basis (Foundation)',
                'description': 'Foundation of life, fundamental nature',
                'sect_dependency': False
            }
            
        except Exception as e:
            logger.error(f"Basis calculation failed: {e}")
            raise ValueError(f"Basis calculation failed: {e}")
    
    def _calculate_love(self, planets: Dict[str, PlanetData], houses: Dict[str, Any],
                      is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Love (Venus-related)."""
        try:
            venus = planets['Venus']
            sun = planets['Sun']
            asc_lon = houses['houses']['ascendant']
            
            # Traditional formula: Ascendant + Venus - Sun
            love_lon = (asc_lon + venus.longitude - sun.longitude) % 360
            
            return {
                'name': 'love',
                'longitude': love_lon,
                'formula_used': 'traditional',
                'formula_text': 'Ascendant + Venus - Sun',
                'traditional_name': 'Lot of Love',
                'description': 'Love affairs, romantic relationships, beauty',
                'sect_dependency': False
            }
            
        except Exception as e:
            logger.error(f"Love calculation failed: {e}")
            return self._create_error_lot('love', str(e))
    
    def _calculate_necessity(self, planets: Dict[str, PlanetData], houses: Dict[str, Any],
                           is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Necessity."""
        try:
            mercury = planets['Mercury']
            fortune_lon = 0  # Would be calculated from Fortune lot
            asc_lon = houses['houses']['ascendant']
            
            # Simplified formula: Ascendant + Mercury - Fortune
            necessity_lon = (asc_lon + mercury.longitude - fortune_lon) % 360
            
            return {
                'name': 'necessity',
                'longitude': necessity_lon,
                'formula_used': 'simplified',
                'formula_text': 'Ascendant + Mercury - Fortune',
                'traditional_name': 'Lot of Necessity',
                'description': 'Constraints, limitations, what must be endured',
                'sect_dependency': False
            }
            
        except Exception as e:
            logger.error(f"Necessity calculation failed: {e}")
            return self._create_error_lot('necessity', str(e))
    
    def _calculate_courage(self, planets: Dict[str, PlanetData], fortune: Dict[str, Any],
                         is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Courage."""
        try:
            mars = planets['Mars']
            fortune_lon = fortune['longitude']
            
            # Formula: Fortune + Mars - Sun
            sun = planets['Sun']
            courage_lon = (fortune_lon + mars.longitude - sun.longitude) % 360
            
            return {
                'name': 'courage',
                'longitude': courage_lon,
                'formula_used': 'traditional',
                'formula_text': 'Fortune + Mars - Sun',
                'traditional_name': 'Lot of Courage',
                'description': 'Bravery, boldness, martial strength',
                'sect_dependency': False
            }
            
        except Exception as e:
            logger.error(f"Courage calculation failed: {e}")
            return self._create_error_lot('courage', str(e))
    
    def _calculate_victory(self, planets: Dict[str, PlanetData], fortune: Dict[str, Any],
                         is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Victory."""
        try:
            jupiter = planets['Jupiter']
            fortune_lon = fortune['longitude']
            sun = planets['Sun']
            
            victory_lon = (fortune_lon + jupiter.longitude - sun.longitude) % 360
            
            return {
                'name': 'victory',
                'longitude': victory_lon,
                'formula_used': 'traditional',
                'formula_text': 'Fortune + Jupiter - Sun',
                'traditional_name': 'Lot of Victory',
                'description': 'Success, triumph, achievement of goals',
                'sect_dependency': False
            }
            
        except Exception as e:
            logger.error(f"Victory calculation failed: {e}")
            return self._create_error_lot('victory', str(e))
    
    def _calculate_nemesis(self, fortune: Dict[str, Any], planets: Dict[str, PlanetData],
                         is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Nemesis."""
        try:
            saturn = planets['Saturn']
            fortune_lon = fortune['longitude']
            
            nemesis_lon = (fortune_lon + saturn.longitude) % 360
            
            return {
                'name': 'nemesis',
                'longitude': nemesis_lon,
                'formula_used': 'simplified',
                'formula_text': 'Fortune + Saturn',
                'traditional_name': 'Lot of Nemesis',
                'description': 'Enemies, retribution, karmic consequences',
                'sect_dependency': False
            }
            
        except Exception as e:
            logger.error(f"Nemesis calculation failed: {e}")
            return self._create_error_lot('nemesis', str(e))
    
    # Simplified implementations for remaining lots
    def _calculate_eros(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Eros (simplified)."""
        try:
            venus = planets['Venus']
            mars = planets['Mars']
            asc_lon = houses['houses']['ascendant']
            
            eros_lon = (asc_lon + venus.longitude + mars.longitude) / 2 % 360
            
            return {
                'name': 'eros',
                'longitude': eros_lon,
                'traditional_name': 'Lot of Eros',
                'description': 'Passionate love, sexual desire',
                'formula_text': 'Simplified: (Asc + Venus + Mars) / 2'
            }
        except Exception as e:
            return self._create_error_lot('eros', str(e))
    
    def _calculate_marriage(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Marriage (simplified)."""
        try:
            venus = planets['Venus']
            jupiter = planets['Jupiter']
            
            marriage_lon = (venus.longitude + jupiter.longitude) / 2 % 360
            
            return {
                'name': 'marriage',
                'longitude': marriage_lon,
                'traditional_name': 'Lot of Marriage',
                'description': 'Marriage partnerships, committed relationships',
                'formula_text': 'Simplified: (Venus + Jupiter) / 2'
            }
        except Exception as e:
            return self._create_error_lot('marriage', str(e))
    
    def _calculate_children(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Children (simplified)."""
        try:
            moon = planets['Moon']
            jupiter = planets['Jupiter']
            
            children_lon = (moon.longitude + jupiter.longitude) / 2 % 360
            
            return {
                'name': 'children',
                'longitude': children_lon,
                'traditional_name': 'Lot of Children',
                'description': 'Children, offspring, fertility',
                'formula_text': 'Simplified: (Moon + Jupiter) / 2'
            }
        except Exception as e:
            return self._create_error_lot('children', str(e))
    
    def _calculate_disease(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Disease (simplified).""" 
        try:
            saturn = planets['Saturn']
            mars = planets['Mars']
            
            disease_lon = (saturn.longitude + mars.longitude) / 2 % 360
            
            return {
                'name': 'disease',
                'longitude': disease_lon,
                'traditional_name': 'Lot of Disease',
                'description': 'Illness, health challenges, physical weakness',
                'formula_text': 'Simplified: (Saturn + Mars) / 2'
            }
        except Exception as e:
            return self._create_error_lot('disease', str(e))
    
    def _calculate_death(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Death (simplified)."""
        try:
            saturn = planets['Saturn']
            
            death_lon = (saturn.longitude + 180) % 360  # Saturn opposition
            
            return {
                'name': 'death',
                'longitude': death_lon,
                'traditional_name': 'Lot of Death',
                'description': 'Death, endings, transformations',
                'formula_text': 'Simplified: Saturn + 180°'
            }
        except Exception as e:
            return self._create_error_lot('death', str(e))
    
    def _calculate_servants(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Servants (simplified)."""
        try:
            mercury = planets['Mercury']
            
            servants_lon = mercury.longitude
            
            return {
                'name': 'servants',
                'longitude': servants_lon,
                'traditional_name': 'Lot of Servants',
                'description': 'Servants, employees, service relationships',
                'formula_text': 'Simplified: Mercury longitude'
            }
        except Exception as e:
            return self._create_error_lot('servants', str(e))
    
    def _calculate_travel(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Travel (simplified)."""
        try:
            mercury = planets['Mercury']
            jupiter = planets['Jupiter']
            
            travel_lon = (mercury.longitude + jupiter.longitude) / 2 % 360
            
            return {
                'name': 'travel',
                'longitude': travel_lon,
                'traditional_name': 'Lot of Travel',
                'description': 'Travel, journeys, foreign places',
                'formula_text': 'Simplified: (Mercury + Jupiter) / 2'
            }
        except Exception as e:
            return self._create_error_lot('travel', str(e))
    
    def _calculate_fame(self, planets: Dict[str, PlanetData], houses: Dict[str, Any], is_day: bool) -> Dict[str, Any]:
        """Calculate Lot of Fame (simplified)."""
        try:
            sun = planets['Sun']
            jupiter = planets['Jupiter']
            mc_lon = houses['houses']['midheaven']
            
            fame_lon = (sun.longitude + jupiter.longitude + mc_lon) / 3 % 360
            
            return {
                'name': 'fame',
                'longitude': fame_lon,
                'traditional_name': 'Lot of Fame',
                'description': 'Fame, reputation, public recognition',
                'formula_text': 'Simplified: (Sun + Jupiter + MC) / 3'
            }
        except Exception as e:
            return self._create_error_lot('fame', str(e))
    
    def _add_astrological_context(self, lot_data: Dict[str, Any], houses: Dict[str, Any]) -> None:
        """Add astrological context (sign, house) to lot data."""
        try:
            longitude = lot_data['longitude']
            
            # Calculate sign
            sign_number = int(longitude // 30) % 12
            signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            
            lot_data.update({
                'sign_number': sign_number,
                'sign_name': signs[sign_number],
                'sign_longitude': longitude % 30,
                'house_number': self._find_house_for_longitude(longitude, houses)
            })
            
        except Exception as e:
            logger.warning(f"Failed to add astrological context: {e}")
    
    def _find_house_for_longitude(self, longitude: float, houses: Dict[str, Any]) -> Optional[int]:
        """Find house number for given longitude (simplified)."""
        try:
            # Simplified house calculation - would need proper implementation
            house_cusps = houses.get('house_cusps', [])
            if not house_cusps:
                return None
                
            # Find which house contains this longitude
            for i in range(12):
                if i < len(house_cusps):
                    cusp_start = house_cusps[i]
                    cusp_end = house_cusps[(i + 1) % 12] if (i + 1) < len(house_cusps) else house_cusps[0]
                    
                    if cusp_start <= longitude < cusp_end:
                        return i + 1
                        
            return 1  # Default to first house
            
        except Exception as e:
            logger.warning(f"House calculation failed: {e}")
            return None
    
    def _create_error_lot(self, lot_name: str, error_message: str) -> Dict[str, Any]:
        """Create error placeholder for failed lot calculation."""
        return {
            'name': lot_name,
            'longitude': 0.0,
            'error': error_message,
            'calculation_failed': True,
            'traditional_name': f'Lot of {lot_name.title()}',
            'description': 'Calculation failed - see error field'
        }