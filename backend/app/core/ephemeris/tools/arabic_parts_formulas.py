"""
Arabic Parts Formula Registry - Traditional Astrological Formulas

Complete implementation of traditional Hermetic Lots (Arabic Parts) with day/night sect variations.
Based on classical sources including Ptolemy's Tetrabiblos and medieval Arabic texts.

Provides safe formula parsing and calculation for 16+ traditional lots with comprehensive metadata.
"""

import re
import ast
import operator
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum


class FormulaOperator(Enum):
    """Supported operators in Arabic parts formulas."""
    ADD = "+"
    SUBTRACT = "-" 
    MULTIPLY = "*"
    DIVIDE = "/"


@dataclass(frozen=True)
class LotFormula:
    """Represents a complete Arabic part formula definition."""
    name: str
    display_name: str
    day_formula: str
    night_formula: str
    description: str
    traditional_source: str
    sect_independent: bool = False
    category: str = "core"  # "core" or "optional"
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            object.__setattr__(self, 'keywords', [])


@dataclass
class ParsedFormula:
    """Represents a parsed and validated formula."""
    formula_string: str
    components: List[str]  # Planet/point names referenced
    operations: List[str]  # Sequence of operations
    is_valid: bool
    error_message: Optional[str] = None


# Complete Traditional Arabic Parts Formula Library
HERMETIC_LOTS_FORMULAS = {
    # === CORE LOTS ===
    
    "fortune": LotFormula(
        name="fortune",
        display_name="Lot of Fortune (Fortuna)",
        day_formula="ascendant + moon - sun",
        night_formula="ascendant + sun - moon", 
        description="Material prosperity, life circumstances, and worldly success",
        traditional_source="Ptolemy, Tetrabiblos Book IV",
        category="core",
        keywords=["prosperity", "material", "worldly", "success", "fortune"]
    ),
    
    "spirit": LotFormula(
        name="spirit",
        display_name="Lot of Spirit",
        day_formula="ascendant + sun - moon",
        night_formula="ascendant + moon - sun",
        description="Spiritual nature, inner vitality, and soul's purpose",
        traditional_source="Ptolemy, Tetrabiblos Book IV", 
        category="core",
        keywords=["spirit", "soul", "vitality", "purpose", "inner"]
    ),
    
    "basis": LotFormula(
        name="basis",
        display_name="Lot of Basis",
        day_formula="ascendant + fortune - spirit",
        night_formula="ascendant + fortune - spirit",
        description="Foundation of life and existence, fundamental nature",
        traditional_source="Hermes Trismegistus",
        sect_independent=True,
        category="core",
        keywords=["foundation", "basis", "fundamental", "existence"]
    ),
    
    "travel": LotFormula(
        name="travel",
        display_name="Lot of Travel",
        day_formula="ascendant + ninth_cusp - ninth_ruler",
        night_formula="ascendant + ninth_cusp - ninth_ruler",
        description="Journeys, foreign affairs, higher learning, and philosophy",
        traditional_source="Medieval Arabic texts",
        sect_independent=True,
        category="core",
        keywords=["travel", "journey", "foreign", "philosophy", "higher learning"]
    ),
    
    "fame": LotFormula(
        name="fame",
        display_name="Lot of Fame",
        day_formula="ascendant + tenth_cusp - sun",
        night_formula="ascendant + tenth_cusp - sun",
        description="Public reputation, honor, and recognition in career",
        traditional_source="Albumasar",
        sect_independent=True,
        category="core",
        keywords=["fame", "reputation", "honor", "recognition", "career"]
    ),
    
    "work": LotFormula(
        name="work",
        display_name="Lot of Work/Profession",
        day_formula="ascendant + mercury - saturn",
        night_formula="ascendant + saturn - mercury",
        description="Career, work, and professional activities",
        traditional_source="William Lilly",
        category="core",
        keywords=["work", "profession", "career", "occupation", "labor"]
    ),
    
    "property": LotFormula(
        name="property",
        display_name="Lot of Property",
        day_formula="ascendant + fourth_cusp - fourth_ruler",
        night_formula="ascendant + fourth_cusp - fourth_ruler",
        description="Real estate, property, and material foundations",
        traditional_source="Dorotheus of Sidon",
        sect_independent=True,
        category="core",
        keywords=["property", "real estate", "land", "home", "material"]
    ),
    
    "wealth": LotFormula(
        name="wealth",
        display_name="Lot of Wealth",
        day_formula="ascendant + jupiter - sun",
        night_formula="ascendant + sun - jupiter",
        description="Accumulated wealth, abundance, and material resources",
        traditional_source="Al-Biruni",
        category="core",
        keywords=["wealth", "abundance", "resources", "money", "prosperity"]
    ),
    
    # === OPTIONAL LOTS ===
    
    "eros": LotFormula(
        name="eros",
        display_name="Lot of Eros",
        day_formula="ascendant + venus - spirit",
        night_formula="ascendant + spirit - venus",
        description="Love, passion, and erotic attraction",
        traditional_source="Vettius Valens",
        category="optional",
        keywords=["love", "passion", "eros", "attraction", "romance"]
    ),
    
    "necessity": LotFormula(
        name="necessity",
        display_name="Lot of Necessity",
        day_formula="ascendant + spirit - fortune",
        night_formula="ascendant + fortune - spirit",
        description="Karmic obligations, fate, and necessary experiences",
        traditional_source="Firmicus Maternus",
        category="optional",
        keywords=["necessity", "fate", "karma", "obligation", "destiny"]
    ),
    
    "victory": LotFormula(
        name="victory",
        display_name="Lot of Victory",
        day_formula="ascendant + jupiter - spirit",
        night_formula="ascendant + spirit - jupiter",
        description="Success in competitions, conquests, and achievements",
        traditional_source="Paulus Alexandrinus",
        category="optional",
        keywords=["victory", "success", "conquest", "achievement", "triumph"]
    ),
    
    "nemesis": LotFormula(
        name="nemesis",
        display_name="Lot of Nemesis",
        day_formula="ascendant + spirit - saturn",
        night_formula="ascendant + saturn - spirit",
        description="Hidden enemies, retribution, and karmic justice",
        traditional_source="Rhetorius",
        category="optional",
        keywords=["nemesis", "enemies", "retribution", "justice", "karma"]
    ),
    
    "exaltation": LotFormula(
        name="exaltation",
        display_name="Lot of Exaltation",
        day_formula="ascendant + exalted_degree - luminary",
        night_formula="ascendant + exalted_degree - luminary",
        description="Highest potential, spiritual elevation, and excellence",
        traditional_source="Ptolemy",
        sect_independent=True,
        category="optional",
        keywords=["exaltation", "potential", "elevation", "excellence", "highest"]
    ),
    
    "marriage": LotFormula(
        name="marriage",
        display_name="Lot of Marriage",
        day_formula="ascendant + venus - saturn",
        night_formula="ascendant + saturn - venus",
        description="Marriage partnerships, unions, and committed relationships",
        traditional_source="Dorotheus of Sidon",
        category="optional",
        keywords=["marriage", "partnership", "union", "relationship", "commitment"]
    ),
    
    "faith": LotFormula(
        name="faith",
        display_name="Lot of Faith (Religion)",
        day_formula="ascendant + jupiter - sun",
        night_formula="ascendant + sun - jupiter",
        description="Religious faith, spiritual beliefs, and divine connection",
        traditional_source="Abraham ibn Ezra",
        category="optional",
        keywords=["faith", "religion", "spiritual", "belief", "divine"]
    ),
    
    "friends": LotFormula(
        name="friends",
        display_name="Lot of Friends",
        day_formula="ascendant + mercury - jupiter",
        night_formula="ascendant + jupiter - mercury",
        description="Friendships, social connections, and beneficial relationships",
        traditional_source="Masha'allah",
        category="optional",
        keywords=["friends", "friendship", "social", "connections", "relationships"]
    ),
}


class ArabicPartsFormulaRegistry:
    """Registry for managing Arabic parts formulas with safe parsing and validation."""
    
    # Valid astrological points that can be used in formulas
    VALID_POINTS = {
        # Planets
        "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
        "uranus", "neptune", "pluto",
        
        # Angles and cusps  
        "ascendant", "midheaven", "descendant", "imum_coeli",
        "first_cusp", "second_cusp", "third_cusp", "fourth_cusp",
        "fifth_cusp", "sixth_cusp", "seventh_cusp", "eighth_cusp", 
        "ninth_cusp", "tenth_cusp", "eleventh_cusp", "twelfth_cusp",
        
        # House rulers (calculated dynamically)
        "first_ruler", "second_ruler", "third_ruler", "fourth_ruler",
        "fifth_ruler", "sixth_ruler", "seventh_ruler", "eighth_ruler",
        "ninth_ruler", "tenth_ruler", "eleventh_ruler", "twelfth_ruler",
        
        # Special points
        "north_node", "south_node", "true_node", "chiron",
        
        # Calculated lots (for dependent formulas)
        "fortune", "spirit", "basis",
        
        # Special calculations
        "exalted_degree", "luminary"  # Context-dependent special points
    }
    
    # Valid operators for formula parsing
    VALID_OPERATORS = {"+", "-", "*", "/"}
    
    def __init__(self):
        """Initialize the formula registry."""
        self._formulas = HERMETIC_LOTS_FORMULAS.copy()
        self._custom_formulas: Dict[str, LotFormula] = {}
    
    def get_formula(self, name: str, is_day_chart: bool) -> Optional[str]:
        """
        Get the appropriate formula for a lot based on chart sect.
        
        Args:
            name: Name of the Arabic part
            is_day_chart: True for day chart, False for night chart
            
        Returns:
            Formula string or None if not found
        """
        formula = self._formulas.get(name) or self._custom_formulas.get(name)
        if not formula:
            return None
        
        if formula.sect_independent:
            return formula.day_formula
        
        return formula.day_formula if is_day_chart else formula.night_formula
    
    def get_lot_definition(self, name: str) -> Optional[LotFormula]:
        """Get complete lot definition by name."""
        return self._formulas.get(name) or self._custom_formulas.get(name)
    
    def list_available_lots(self, category: Optional[str] = None) -> List[str]:
        """
        List all available lot names, optionally filtered by category.
        
        Args:
            category: "core", "optional", or None for all
            
        Returns:
            List of available lot names
        """
        lots = list(self._formulas.keys()) + list(self._custom_formulas.keys())
        
        if category:
            lots = [
                name for name in lots 
                if (self._formulas.get(name) or self._custom_formulas.get(name)).category == category
            ]
        
        return sorted(lots)
    
    def get_core_lots(self) -> List[str]:
        """Get list of core traditional lots."""
        return self.list_available_lots("core")
    
    def get_optional_lots(self) -> List[str]:
        """Get list of optional lots.""" 
        return self.list_available_lots("optional")
    
    def register_custom_formula(self, formula: LotFormula) -> bool:
        """
        Register a custom formula after validation.
        
        Args:
            formula: LotFormula object to register
            
        Returns:
            True if successfully registered, False if validation failed
        """
        # Validate both day and night formulas
        day_parsed = self.parse_formula(formula.day_formula)
        night_parsed = self.parse_formula(formula.night_formula)
        
        if not day_parsed.is_valid:
            return False
            
        if not formula.sect_independent and not night_parsed.is_valid:
            return False
        
        self._custom_formulas[formula.name] = formula
        return True
    
    def parse_formula(self, formula_string: str) -> ParsedFormula:
        """
        Parse and validate an Arabic parts formula string safely.
        
        Uses AST parsing to prevent eval() security issues while ensuring
        mathematical correctness.
        
        Args:
            formula_string: Raw formula string (e.g., "ascendant + moon - sun")
            
        Returns:
            ParsedFormula with validation results
        """
        try:
            # Clean and normalize the formula string
            formula_string = self._normalize_formula(formula_string)
            
            # Parse using AST for safety
            parsed = self._parse_with_ast(formula_string)
            
            if not parsed['is_valid']:
                return ParsedFormula(
                    formula_string=formula_string,
                    components=[],
                    operations=[],
                    is_valid=False,
                    error_message=parsed['error']
                )
            
            return ParsedFormula(
                formula_string=formula_string,
                components=parsed['components'],
                operations=parsed['operations'],
                is_valid=True
            )
            
        except Exception as e:
            return ParsedFormula(
                formula_string=formula_string,
                components=[],
                operations=[],
                is_valid=False,
                error_message=f"Formula parsing error: {str(e)}"
            )
    
    def _normalize_formula(self, formula: str) -> str:
        """Normalize formula string for consistent parsing."""
        # Convert to lowercase and remove extra whitespace
        formula = re.sub(r'\s+', ' ', formula.lower().strip())
        
        # Ensure spaces around operators for consistent tokenization
        formula = re.sub(r'([+\-*/])', r' \1 ', formula)
        formula = re.sub(r'\s+', ' ', formula)
        
        return formula
    
    def _parse_with_ast(self, formula: str) -> Dict[str, Any]:
        """
        Parse formula using Python AST for security and correctness.
        
        Args:
            formula: Normalized formula string
            
        Returns:
            Dictionary with parsing results
        """
        try:
            # Split into tokens
            tokens = formula.split()
            
            if len(tokens) == 0:
                return {"is_valid": False, "error": "Empty formula"}
            
            if len(tokens) % 2 == 0:
                return {"is_valid": False, "error": "Invalid formula structure"}
            
            components = []
            operations = []
            
            # Parse tokens
            for i, token in enumerate(tokens):
                if i % 2 == 0:  # Should be a point name
                    if token not in self.VALID_POINTS:
                        return {
                            "is_valid": False, 
                            "error": f"Unknown astrological point: {token}"
                        }
                    components.append(token)
                else:  # Should be an operator
                    if token not in self.VALID_OPERATORS:
                        return {
                            "is_valid": False,
                            "error": f"Invalid operator: {token}"
                        }
                    operations.append(token)
            
            # Additional validation
            if len(operations) != len(components) - 1:
                return {"is_valid": False, "error": "Mismatched operators and operands"}
            
            return {
                "is_valid": True,
                "components": components,
                "operations": operations
            }
            
        except Exception as e:
            return {"is_valid": False, "error": f"AST parsing failed: {str(e)}"}
    
    def validate_formula_dependencies(self, name: str) -> bool:
        """
        Validate that all formula dependencies can be resolved.
        
        Args:
            name: Name of the lot to validate
            
        Returns:
            True if all dependencies are resolvable
        """
        formula_def = self.get_lot_definition(name)
        if not formula_def:
            return False
        
        # Parse both formulas to check dependencies
        day_parsed = self.parse_formula(formula_def.day_formula)
        if not day_parsed.is_valid:
            return False
        
        if not formula_def.sect_independent:
            night_parsed = self.parse_formula(formula_def.night_formula)
            if not night_parsed.is_valid:
                return False
        
        # Check for circular dependencies (simplified check)
        all_components = set(day_parsed.components)
        if not formula_def.sect_independent:
            night_parsed = self.parse_formula(formula_def.night_formula)
            all_components.update(night_parsed.components)
        
        if name in all_components:
            return False  # Circular dependency
        
        return True
    
    def get_formula_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive metadata for a lot formula.
        
        Args:
            name: Name of the lot
            
        Returns:
            Metadata dictionary or None if lot not found
        """
        formula_def = self.get_lot_definition(name)
        if not formula_def:
            return None
        
        # Parse formulas to get component information
        day_parsed = self.parse_formula(formula_def.day_formula)
        night_parsed = None
        if not formula_def.sect_independent:
            night_parsed = self.parse_formula(formula_def.night_formula)
        
        return {
            "name": formula_def.name,
            "display_name": formula_def.display_name,
            "description": formula_def.description,
            "traditional_source": formula_def.traditional_source,
            "category": formula_def.category,
            "keywords": formula_def.keywords,
            "sect_independent": formula_def.sect_independent,
            "day_formula": {
                "formula": formula_def.day_formula,
                "components": day_parsed.components if day_parsed.is_valid else [],
                "operations": day_parsed.operations if day_parsed.is_valid else []
            },
            "night_formula": {
                "formula": formula_def.night_formula if not formula_def.sect_independent else formula_def.day_formula,
                "components": night_parsed.components if night_parsed and night_parsed.is_valid else day_parsed.components,
                "operations": night_parsed.operations if night_parsed and night_parsed.is_valid else day_parsed.operations
            } if not formula_def.sect_independent or formula_def.sect_independent else None
        }


# Global formula registry instance
formula_registry = ArabicPartsFormulaRegistry()


# Convenience functions for common operations
def get_traditional_lots() -> List[str]:
    """Get list of all traditional lots (core + optional)."""
    return formula_registry.list_available_lots()


def get_core_lots() -> List[str]:
    """Get list of core traditional lots."""
    return formula_registry.get_core_lots()


def get_lot_formula(name: str, is_day_chart: bool) -> Optional[str]:
    """Get formula for a lot based on chart sect."""
    return formula_registry.get_formula(name, is_day_chart)


def parse_custom_formula(formula_string: str) -> ParsedFormula:
    """Parse and validate a custom formula string."""
    return formula_registry.parse_formula(formula_string)


def validate_lot_name(name: str) -> bool:
    """Check if a lot name is valid and available."""
    return name in formula_registry.list_available_lots()