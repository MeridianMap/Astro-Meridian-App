"""
Orb Configuration Systems - Professional Astrological Orb Standards

Provides comprehensive orb systems for aspect calculations:
- Traditional orbs (classical astrology)
- Modern orbs (contemporary practice) 
- Tight orbs (research-grade precision)
- Custom orb system support

Based on established astrological traditions and professional software standards.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass

from .aspects import OrbConfiguration


# Traditional Orb System (Classical Astrology)
TRADITIONAL_ORBS = {
    'conjunction': {
        'sun': 8.0, 'moon': 8.0, 'mercury': 6.0, 'venus': 6.0, 'mars': 6.0,
        'jupiter': 6.0, 'saturn': 6.0, 'uranus': 5.0, 'neptune': 5.0, 'pluto': 5.0,
        'true_node': 5.0, 'chiron': 4.0, 'default': 6.0
    },
    'opposition': {
        'sun': 8.0, 'moon': 8.0, 'mercury': 6.0, 'venus': 6.0, 'mars': 6.0,
        'jupiter': 6.0, 'saturn': 6.0, 'uranus': 5.0, 'neptune': 5.0, 'pluto': 5.0,
        'true_node': 5.0, 'chiron': 4.0, 'default': 6.0
    },
    'trine': {
        'sun': 6.0, 'moon': 6.0, 'mercury': 5.0, 'venus': 5.0, 'mars': 5.0,
        'jupiter': 5.0, 'saturn': 5.0, 'uranus': 4.0, 'neptune': 4.0, 'pluto': 4.0,
        'true_node': 4.0, 'chiron': 3.5, 'default': 5.0
    },
    'square': {
        'sun': 6.0, 'moon': 6.0, 'mercury': 5.0, 'venus': 5.0, 'mars': 5.0,
        'jupiter': 5.0, 'saturn': 5.0, 'uranus': 4.0, 'neptune': 4.0, 'pluto': 4.0,
        'true_node': 4.0, 'chiron': 3.5, 'default': 5.0
    },
    'sextile': {
        'sun': 4.0, 'moon': 4.0, 'mercury': 3.5, 'venus': 3.5, 'mars': 3.5,
        'jupiter': 3.5, 'saturn': 3.5, 'uranus': 3.0, 'neptune': 3.0, 'pluto': 3.0,
        'true_node': 3.0, 'chiron': 2.5, 'default': 3.5
    },
    'semi_sextile': {
        'sun': 2.0, 'moon': 2.0, 'mercury': 1.5, 'venus': 1.5, 'mars': 1.5,
        'jupiter': 1.5, 'saturn': 1.5, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 1.0, 'default': 1.5
    },
    'quincunx': {
        'sun': 2.0, 'moon': 2.0, 'mercury': 1.5, 'venus': 1.5, 'mars': 1.5,
        'jupiter': 1.5, 'saturn': 1.5, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 1.0, 'default': 1.5
    },
    'semi_square': {
        'sun': 2.0, 'moon': 2.0, 'mercury': 1.5, 'venus': 1.5, 'mars': 1.5,
        'jupiter': 1.5, 'saturn': 1.5, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 1.0, 'default': 1.5
    },
    'sesquiquadrate': {
        'sun': 2.0, 'moon': 2.0, 'mercury': 1.5, 'venus': 1.5, 'mars': 1.5,
        'jupiter': 1.5, 'saturn': 1.5, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 1.0, 'default': 1.5
    }
}

# Modern Orb System (Contemporary Practice - More Generous)
MODERN_ORBS = {
    'conjunction': {
        'sun': 10.0, 'moon': 12.0, 'mercury': 8.0, 'venus': 8.0, 'mars': 8.0,
        'jupiter': 8.0, 'saturn': 8.0, 'uranus': 7.0, 'neptune': 7.0, 'pluto': 7.0,
        'true_node': 7.0, 'chiron': 6.0, 'default': 8.0
    },
    'opposition': {
        'sun': 10.0, 'moon': 12.0, 'mercury': 8.0, 'venus': 8.0, 'mars': 8.0,
        'jupiter': 8.0, 'saturn': 8.0, 'uranus': 7.0, 'neptune': 7.0, 'pluto': 7.0,
        'true_node': 7.0, 'chiron': 6.0, 'default': 8.0
    },
    'trine': {
        'sun': 8.0, 'moon': 8.0, 'mercury': 6.0, 'venus': 6.0, 'mars': 6.0,
        'jupiter': 6.0, 'saturn': 6.0, 'uranus': 5.0, 'neptune': 5.0, 'pluto': 5.0,
        'true_node': 5.0, 'chiron': 4.5, 'default': 6.0
    },
    'square': {
        'sun': 8.0, 'moon': 8.0, 'mercury': 6.0, 'venus': 6.0, 'mars': 6.0,
        'jupiter': 6.0, 'saturn': 6.0, 'uranus': 5.0, 'neptune': 5.0, 'pluto': 5.0,
        'true_node': 5.0, 'chiron': 4.5, 'default': 6.0
    },
    'sextile': {
        'sun': 6.0, 'moon': 6.0, 'mercury': 4.5, 'venus': 4.5, 'mars': 4.5,
        'jupiter': 4.5, 'saturn': 4.5, 'uranus': 4.0, 'neptune': 4.0, 'pluto': 4.0,
        'true_node': 4.0, 'chiron': 3.5, 'default': 4.5
    },
    'semi_sextile': {
        'sun': 3.0, 'moon': 3.0, 'mercury': 2.5, 'venus': 2.5, 'mars': 2.5,
        'jupiter': 2.5, 'saturn': 2.5, 'uranus': 2.0, 'neptune': 2.0, 'pluto': 2.0,
        'true_node': 2.0, 'chiron': 1.5, 'default': 2.5
    },
    'quincunx': {
        'sun': 3.0, 'moon': 3.0, 'mercury': 2.5, 'venus': 2.5, 'mars': 2.5,
        'jupiter': 2.5, 'saturn': 2.5, 'uranus': 2.0, 'neptune': 2.0, 'pluto': 2.0,
        'true_node': 2.0, 'chiron': 1.5, 'default': 2.5
    },
    'semi_square': {
        'sun': 3.0, 'moon': 3.0, 'mercury': 2.5, 'venus': 2.5, 'mars': 2.5,
        'jupiter': 2.5, 'saturn': 2.5, 'uranus': 2.0, 'neptune': 2.0, 'pluto': 2.0,
        'true_node': 2.0, 'chiron': 1.5, 'default': 2.5
    },
    'sesquiquadrate': {
        'sun': 3.0, 'moon': 3.0, 'mercury': 2.5, 'venus': 2.5, 'mars': 2.5,
        'jupiter': 2.5, 'saturn': 2.5, 'uranus': 2.0, 'neptune': 2.0, 'pluto': 2.0,
        'true_node': 2.0, 'chiron': 1.5, 'default': 2.5
    }
}

# Tight Orb System (Research-Grade Precision)
TIGHT_ORBS = {
    'conjunction': {
        'sun': 5.0, 'moon': 5.0, 'mercury': 4.0, 'venus': 4.0, 'mars': 4.0,
        'jupiter': 4.0, 'saturn': 4.0, 'uranus': 3.0, 'neptune': 3.0, 'pluto': 3.0,
        'true_node': 3.0, 'chiron': 2.5, 'default': 4.0
    },
    'opposition': {
        'sun': 5.0, 'moon': 5.0, 'mercury': 4.0, 'venus': 4.0, 'mars': 4.0,
        'jupiter': 4.0, 'saturn': 4.0, 'uranus': 3.0, 'neptune': 3.0, 'pluto': 3.0,
        'true_node': 3.0, 'chiron': 2.5, 'default': 4.0
    },
    'trine': {
        'sun': 4.0, 'moon': 4.0, 'mercury': 3.0, 'venus': 3.0, 'mars': 3.0,
        'jupiter': 3.0, 'saturn': 3.0, 'uranus': 2.5, 'neptune': 2.5, 'pluto': 2.5,
        'true_node': 2.5, 'chiron': 2.0, 'default': 3.0
    },
    'square': {
        'sun': 4.0, 'moon': 4.0, 'mercury': 3.0, 'venus': 3.0, 'mars': 3.0,
        'jupiter': 3.0, 'saturn': 3.0, 'uranus': 2.5, 'neptune': 2.5, 'pluto': 2.5,
        'true_node': 2.5, 'chiron': 2.0, 'default': 3.0
    },
    'sextile': {
        'sun': 3.0, 'moon': 3.0, 'mercury': 2.5, 'venus': 2.5, 'mars': 2.5,
        'jupiter': 2.5, 'saturn': 2.5, 'uranus': 2.0, 'neptune': 2.0, 'pluto': 2.0,
        'true_node': 2.0, 'chiron': 1.5, 'default': 2.5
    },
    'semi_sextile': {
        'sun': 1.5, 'moon': 1.5, 'mercury': 1.0, 'venus': 1.0, 'mars': 1.0,
        'jupiter': 1.0, 'saturn': 1.0, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 0.5, 'default': 1.0
    },
    'quincunx': {
        'sun': 1.5, 'moon': 1.5, 'mercury': 1.0, 'venus': 1.0, 'mars': 1.0,
        'jupiter': 1.0, 'saturn': 1.0, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 0.5, 'default': 1.0
    },
    'semi_square': {
        'sun': 1.5, 'moon': 1.5, 'mercury': 1.0, 'venus': 1.0, 'mars': 1.0,
        'jupiter': 1.0, 'saturn': 1.0, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 0.5, 'default': 1.0
    },
    'sesquiquadrate': {
        'sun': 1.5, 'moon': 1.5, 'mercury': 1.0, 'venus': 1.0, 'mars': 1.0,
        'jupiter': 1.0, 'saturn': 1.0, 'uranus': 1.0, 'neptune': 1.0, 'pluto': 1.0,
        'true_node': 1.0, 'chiron': 0.5, 'default': 1.0
    }
}


class OrbSystemManager:
    """Manages orb configuration systems for aspect calculations."""
    
    def __init__(self):
        """Initialize orb system manager with predefined systems."""
        self._preset_systems = {
            'traditional': TRADITIONAL_ORBS,
            'modern': MODERN_ORBS, 
            'tight': TIGHT_ORBS
        }
    
    def load_orb_preset(self, preset_name: str) -> OrbConfiguration:
        """
        Load a predefined orb system configuration.
        
        Args:
            preset_name: Name of preset system ('traditional', 'modern', 'tight')
            
        Returns:
            OrbConfiguration object ready for AspectCalculator
            
        Raises:
            ValueError: If preset name is not recognized
        """
        if preset_name not in self._preset_systems:
            available = ', '.join(self._preset_systems.keys())
            raise ValueError(
                f"Unknown orb preset '{preset_name}'. "
                f"Available presets: {available}"
            )
        
        return OrbConfiguration(
            preset_name=preset_name,
            aspect_orbs=self._preset_systems[preset_name].copy(),
            applying_factor=1.0,
            separating_factor=1.0
        )
    
    def get_orb_preset(self, preset_name: str) -> OrbConfiguration:
        """Alias for load_orb_preset for backward compatibility."""
        return self.load_orb_preset(preset_name)
    
    def create_custom_orb_config(
        self, 
        custom_orbs: Dict[str, Dict[str, float]],
        base_preset: str = 'traditional',
        applying_factor: float = 1.0,
        separating_factor: float = 1.0
    ) -> OrbConfiguration:
        """
        Create a custom orb configuration.
        
        Args:
            base_preset: Base preset to start with
            custom_orbs: Custom orb overrides
            applying_factor: Multiplier for applying aspects
            separating_factor: Multiplier for separating aspects
            
        Returns:
            Custom OrbConfiguration object
        """
        # Start with base preset
        base_config = self.load_orb_preset(base_preset)
        
        # Apply custom overrides if provided
        if custom_orbs:
            base_config = self._merge_orb_configs(base_config, custom_orbs)
        
        # Update factors
        base_config.applying_factor = applying_factor
        base_config.separating_factor = separating_factor
        base_config.preset_name = 'custom'
        
        return base_config
    
    def _merge_orb_configs(self, base_config: OrbConfiguration, custom_orbs: Dict[str, Dict[str, float]]) -> OrbConfiguration:
        """
        Merge custom orbs with base configuration.
        
        Args:
            base_config: Base orb configuration
            custom_orbs: Custom orb overrides
            
        Returns:
            Merged orb configuration
        """
        merged_orbs = base_config.aspect_orbs.copy()
        
        for aspect_type, aspect_orbs in custom_orbs.items():
            if aspect_type not in merged_orbs:
                merged_orbs[aspect_type] = {}
            
            merged_orbs[aspect_type].update(aspect_orbs)
        
        return OrbConfiguration(
            preset_name='custom',
            aspect_orbs=merged_orbs,
            applying_factor=base_config.applying_factor,
            separating_factor=base_config.separating_factor
        )
    
    def validate_custom_orbs(self, custom_orbs: Dict[str, Any]) -> bool:
        """
        Validate custom orb configuration structure.
        
        Args:
            custom_orbs: Custom orb configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check overall structure
            if not isinstance(custom_orbs, dict):
                return False
            
            # Check each aspect type
            for aspect_type, planet_orbs in custom_orbs.items():
                if not isinstance(aspect_type, str):
                    return False
                
                if not isinstance(planet_orbs, dict):
                    return False
                
                # Check each planet orb
                for planet, orb_value in planet_orbs.items():
                    if not isinstance(planet, str):
                        return False
                    
                    if not isinstance(orb_value, (int, float)):
                        return False
                    
                    # Orbs should be positive and reasonable
                    if orb_value < 0 or orb_value > 30:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _merge_orb_configs(
        self, 
        base_config: OrbConfiguration, 
        custom_orbs: Dict[str, Dict[str, float]]
    ) -> OrbConfiguration:
        """Merge custom orbs into base configuration."""
        merged_orbs = base_config.aspect_orbs.copy()
        
        for aspect_type, planet_orbs in custom_orbs.items():
            if aspect_type in merged_orbs:
                merged_orbs[aspect_type].update(planet_orbs)
            else:
                merged_orbs[aspect_type] = planet_orbs.copy()
        
        return OrbConfiguration(
            preset_name=base_config.preset_name,
            aspect_orbs=merged_orbs,
            applying_factor=base_config.applying_factor,
            separating_factor=base_config.separating_factor
        )
    
    def get_available_presets(self) -> list[str]:
        """Get list of available orb preset names."""
        return list(self._preset_systems.keys())
    
    def get_preset_info(self, preset_name: str) -> Dict[str, Any]:
        """
        Get information about a specific orb preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Dictionary with preset information and sample orbs
        """
        if preset_name not in self._preset_systems:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        preset_data = self._preset_systems[preset_name]
        
        # Get sample orbs for major aspects
        major_aspects = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
        sample_orbs = {}
        
        for aspect in major_aspects:
            if aspect in preset_data:
                sample_orbs[aspect] = {
                    'sun_moon': f"{preset_data[aspect]['sun']}-{preset_data[aspect]['moon']}°",
                    'planets': f"{preset_data[aspect]['default']}°",
                }
        
        descriptions = {
            'traditional': 'Classical astrological orbs based on traditional sources',
            'modern': 'Contemporary orbs used in modern astrological practice',
            'tight': 'Research-grade tight orbs for precision work'
        }
        
        return {
            'name': preset_name,
            'description': descriptions.get(preset_name, ''),
            'sample_orbs': sample_orbs,
            'total_aspects': len(preset_data)
        }


# Convenience functions for direct usage
def get_traditional_orbs() -> OrbConfiguration:
    """Get traditional orb configuration."""
    return OrbSystemManager().load_orb_preset('traditional')


def get_modern_orbs() -> OrbConfiguration:
    """Get modern orb configuration.""" 
    return OrbSystemManager().load_orb_preset('modern')


def get_tight_orbs() -> OrbConfiguration:
    """Get tight orb configuration."""
    return OrbSystemManager().load_orb_preset('tight')


def create_custom_orbs(
    base_preset: str = 'traditional',
    **custom_overrides: Dict[str, float]
) -> OrbConfiguration:
    """
    Create custom orb configuration with simple overrides.
    
    Example:
        create_custom_orbs(
            base_preset='traditional',
            sun_conjunction=10.0,
            moon_opposition=9.0
        )
    """
    manager = OrbSystemManager()
    
    # Convert simple overrides to full structure
    if custom_overrides:
        custom_orbs = {}
        for key, value in custom_overrides.items():
            if '_' in key:
                planet, aspect = key.split('_', 1)
                if aspect not in custom_orbs:
                    custom_orbs[aspect] = {}
                custom_orbs[aspect][planet] = value
        
        return manager.create_custom_orb_config(
            base_preset=base_preset,
            custom_orbs=custom_orbs
        )
    
    return manager.load_orb_preset(base_preset)