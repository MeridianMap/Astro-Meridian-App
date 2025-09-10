"""
Visualization Metadata System for Enhanced ACG

This module provides comprehensive visualization metadata generation for
enhanced ACG features including motion-based styling, aspect line visualization,
and interactive behavior specifications for frontend integration.

Supports multiple frontend frameworks:
- Three.js for 3D globe visualization  
- D3.js for 2D map visualization
- Leaflet for interactive maps
- Custom visualization frameworks
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from .enhanced_metadata import RetrogradeAwareLineMetadata, MotionStatus, PlanetaryDignity
from .aspect_lines import AspectLineFeature, AspectLinePoint
from extracted.systems.ephemeris_utils.tools.aspects import AspectType

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class VisualizationFramework(Enum):
    """Supported visualization frameworks."""
    THREE_JS = "three_js"
    D3_JS = "d3_js"
    LEAFLET = "leaflet"
    MAPBOX = "mapbox"
    GENERIC = "generic"


class AnimationType(Enum):
    """Supported animation types for visualization."""
    NONE = "none"
    PULSE = "pulse"
    FADE = "fade"
    GLOW = "glow"
    MOTION_TRAIL = "motion_trail"
    STATION_APPROACH = "station_approach"


@dataclass
class StyleMetadata:
    """Comprehensive styling metadata for visualization."""
    
    # Base styling
    color: str = "#3366cc"
    opacity: float = 0.8
    line_width: float = 2.0
    line_style: str = "solid"  # solid, dashed, dotted
    
    # Advanced styling
    glow_effect: bool = False
    glow_color: Optional[str] = None
    glow_intensity: float = 1.0
    shadow_effect: bool = False
    gradient_colors: Optional[List[str]] = None
    
    # Interactive properties
    hover_color: str = "#ffcc00"
    hover_opacity: float = 1.0
    hover_line_width: float = 3.0
    clickable: bool = True
    selectable: bool = True
    
    # Animation properties
    animation_type: AnimationType = AnimationType.NONE
    animation_duration: float = 1000.0  # milliseconds
    animation_delay: float = 0.0
    animation_easing: str = "ease-in-out"
    
    # Z-index and layering
    z_index: int = 1
    render_order: int = 0
    layer_group: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "base_style": {
                "color": self.color,
                "opacity": self.opacity,
                "line_width": self.line_width,
                "line_style": self.line_style
            },
            "effects": {
                "glow": {
                    "enabled": self.glow_effect,
                    "color": self.glow_color,
                    "intensity": self.glow_intensity
                },
                "shadow": self.shadow_effect,
                "gradient_colors": self.gradient_colors
            },
            "interactive": {
                "hover": {
                    "color": self.hover_color,
                    "opacity": self.hover_opacity,
                    "line_width": self.hover_line_width
                },
                "clickable": self.clickable,
                "selectable": self.selectable
            },
            "animation": {
                "type": self.animation_type.value,
                "duration": self.animation_duration,
                "delay": self.animation_delay,
                "easing": self.animation_easing
            },
            "layering": {
                "z_index": self.z_index,
                "render_order": self.render_order,
                "layer_group": self.layer_group
            }
        }


@dataclass
class InteractiveMetadata:
    """Interactive behavior metadata for visualization."""
    
    # Tooltip configuration
    tooltip_enabled: bool = True
    tooltip_template: str = "default"
    tooltip_position: str = "auto"  # auto, top, bottom, left, right
    tooltip_data: Dict[str, Any] = field(default_factory=dict)
    
    # Click/selection behavior
    on_click_action: str = "select"  # select, highlight, info, custom
    on_hover_action: str = "highlight"  # highlight, tooltip, preview
    selection_group: Optional[str] = None
    
    # Context menu options
    context_menu_enabled: bool = False
    context_menu_items: List[Dict[str, str]] = field(default_factory=list)
    
    # Keyboard interactions
    keyboard_shortcuts: Dict[str, str] = field(default_factory=dict)
    
    # Accessibility
    aria_label: str = ""
    aria_description: str = ""
    focus_indicator: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tooltip": {
                "enabled": self.tooltip_enabled,
                "template": self.tooltip_template,
                "position": self.tooltip_position,
                "data": self.tooltip_data
            },
            "interactions": {
                "click_action": self.on_click_action,
                "hover_action": self.on_hover_action,
                "selection_group": self.selection_group
            },
            "context_menu": {
                "enabled": self.context_menu_enabled,
                "items": self.context_menu_items
            },
            "keyboard": self.keyboard_shortcuts,
            "accessibility": {
                "label": self.aria_label,
                "description": self.aria_description,
                "focus_indicator": self.focus_indicator
            }
        }


@dataclass
class LegendData:
    """Legend data for visualization."""
    
    title: str = "ACG Lines"
    items: List[Dict[str, Any]] = field(default_factory=list)
    position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right
    collapsible: bool = True
    default_collapsed: bool = False
    
    # Styling
    background_color: str = "rgba(255, 255, 255, 0.9)"
    border_color: str = "#cccccc"
    text_color: str = "#333333"
    font_size: str = "12px"
    
    def add_motion_legend(
        self,
        motion_filters: List[str],
        color_scheme: Dict[str, str]
    ) -> None:
        """Add motion-based legend items."""
        motion_descriptions = {
            "direct": "Planet moving forward through zodiac",
            "retrograde": "Planet moving backward through zodiac", 
            "stationary": "Planet changing direction (station)"
        }
        
        for motion in motion_filters:
            if motion in color_scheme and motion in motion_descriptions:
                self.items.append({
                    "label": motion.replace("_", " ").title(),
                    "color": color_scheme[motion],
                    "line_style": "dashed" if motion == "retrograde" else "solid",
                    "description": motion_descriptions[motion],
                    "category": "motion"
                })
    
    def add_aspect_legend(
        self,
        aspect_types: List[AspectType],
        color_scheme: Dict[str, str]
    ) -> None:
        """Add aspect-based legend items."""
        aspect_descriptions = {
            AspectType.CONJUNCTION: "0° - Unity and blending",
            AspectType.SEXTILE: "60° - Opportunity and cooperation",
            AspectType.SQUARE: "90° - Challenge and tension",
            AspectType.TRINE: "120° - Harmony and flow",
            AspectType.OPPOSITION: "180° - Polarity and balance"
        }
        
        for aspect in aspect_types:
            aspect_name = aspect.name.lower()
            if aspect_name in color_scheme:
                self.items.append({
                    "label": aspect.name.replace("_", " ").title(),
                    "color": color_scheme[aspect_name],
                    "line_style": "solid",
                    "description": aspect_descriptions.get(aspect, ""),
                    "category": "aspects"
                })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "items": self.items,
            "position": self.position,
            "collapsible": self.collapsible,
            "default_collapsed": self.default_collapsed,
            "styling": {
                "background_color": self.background_color,
                "border_color": self.border_color,
                "text_color": self.text_color,
                "font_size": self.font_size
            }
        }


class VisualizationMetadataGenerator:
    """
    Generator for comprehensive visualization metadata.
    
    Creates styling, interaction, and animation metadata optimized
    for different frontend visualization frameworks.
    """
    
    # Color schemes for different visualization contexts
    COLOR_SCHEMES = {
        "motion_default": {
            "direct": "#3366cc",
            "retrograde": "#cc3333", 
            "stationary": "#ffaa00"
        },
        "motion_pastel": {
            "direct": "#6699ff",
            "retrograde": "#ff6666",
            "stationary": "#ffcc66"
        },
        "motion_high_contrast": {
            "direct": "#0000ff",
            "retrograde": "#ff0000",
            "stationary": "#ff8800"
        },
        "aspects_traditional": {
            "conjunction": "#ff0000",  # Red
            "sextile": "#00ff00",      # Green
            "square": "#ff8800",       # Orange
            "trine": "#0088ff",        # Blue
            "opposition": "#8800ff"    # Purple
        },
        "aspects_modern": {
            "conjunction": "#e74c3c",  # Modern red
            "sextile": "#2ecc71",      # Modern green
            "square": "#f39c12",       # Modern orange
            "trine": "#3498db",        # Modern blue
            "opposition": "#9b59b6"    # Modern purple
        }
    }
    
    # Framework-specific styling templates
    FRAMEWORK_TEMPLATES = {
        VisualizationFramework.THREE_JS: {
            "material_type": "LineBasicMaterial",
            "geometry_type": "BufferGeometry",
            "render_order": True,
            "depth_test": True,
            "transparent": True
        },
        VisualizationFramework.D3_JS: {
            "stroke_dasharray": "none",
            "stroke_linecap": "round",
            "stroke_linejoin": "round",
            "fill": "none"
        },
        VisualizationFramework.LEAFLET: {
            "weight": 2,
            "smoothFactor": 1.0,
            "noClip": False,
            "bubblingMouseEvents": True
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_motion_styling(
        self,
        motion_status: MotionStatus,
        planet_name: str,
        retrograde_metadata: Optional[RetrogradeAwareLineMetadata] = None,
        color_scheme: str = "motion_default",
        framework: VisualizationFramework = VisualizationFramework.GENERIC
    ) -> StyleMetadata:
        """
        Generate comprehensive styling metadata for motion visualization.
        
        Args:
            motion_status: Planetary motion status
            planet_name: Name of the planet
            retrograde_metadata: Enhanced retrograde metadata
            color_scheme: Color scheme to use
            framework: Target visualization framework
            
        Returns:
            StyleMetadata with motion-based styling
        """
        try:
            # Get color scheme
            colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["motion_default"])
            motion_key = motion_status.value.replace("_", "")
            
            # Base styling from motion status
            style = StyleMetadata(
                color=colors.get(motion_key, colors["direct"]),
                opacity=0.8,
                line_width=2.0,
                line_style="solid"
            )
            
            # Motion-specific enhancements
            if motion_status == MotionStatus.RETROGRADE:
                style.line_style = "dashed"
                style.glow_effect = True
                style.glow_color = style.color
                style.glow_intensity = 1.2
                style.animation_type = AnimationType.PULSE
                style.animation_duration = 2000.0
            
            elif motion_status in [MotionStatus.STATIONARY_DIRECT, MotionStatus.STATIONARY_RETROGRADE]:
                style.line_style = "dotted"
                style.glow_effect = True
                style.animation_type = AnimationType.PULSE
                style.animation_duration = 1000.0
                style.z_index = 10  # Higher priority for stations
            
            # Enhanced metadata adjustments
            if retrograde_metadata:
                # Speed-based adjustments
                if retrograde_metadata.motion_speed_percentile < 20:  # Very slow
                    style.opacity *= 0.8
                    style.line_width *= 0.8
                elif retrograde_metadata.motion_speed_percentile > 80:  # Very fast
                    style.opacity *= 1.1
                    style.line_width *= 1.2
                
                # Station approach enhancements
                if retrograde_metadata.is_approaching_station:
                    style.animation_type = AnimationType.STATION_APPROACH
                    style.glow_effect = True
                    style.z_index = 15
            
            # Framework-specific adjustments
            self._apply_framework_styling(style, framework)
            
            return style
            
        except Exception as e:
            self.logger.error(f"Failed to generate motion styling: {e}")
            return StyleMetadata()  # Return default styling
    
    def generate_aspect_styling(
        self,
        aspect_type: AspectType,
        line_strength: float,
        angle_name: str,
        color_scheme: str = "aspects_traditional",
        framework: VisualizationFramework = VisualizationFramework.GENERIC
    ) -> StyleMetadata:
        """
        Generate styling metadata for aspect-to-angle lines.
        
        Args:
            aspect_type: Type of aspect
            line_strength: Strength of aspect line (0-1)
            angle_name: Name of angle (MC, ASC, etc.)
            color_scheme: Color scheme to use
            framework: Target visualization framework
            
        Returns:
            StyleMetadata with aspect-based styling
        """
        try:
            # Get color scheme
            colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["aspects_traditional"])
            aspect_key = aspect_type.name.lower()
            
            # Base styling
            style = StyleMetadata(
                color=colors.get(aspect_key, "#3366cc"),
                opacity=0.6 + (line_strength * 0.3),  # Stronger aspects more opaque
                line_width=1.5 + (line_strength * 1.0),  # Stronger aspects wider
                line_style="solid"
            )
            
            # Aspect-specific styling
            if aspect_type == AspectType.CONJUNCTION:
                style.glow_effect = True
                style.glow_intensity = 1.5
                style.z_index = 8
            elif aspect_type == AspectType.OPPOSITION:
                style.line_style = "dashed"
                style.z_index = 7
            elif aspect_type in [AspectType.TRINE, AspectType.SEXTILE]:
                style.opacity *= 1.1  # Harmonious aspects slightly more visible
                style.z_index = 6
            elif aspect_type == AspectType.SQUARE:
                style.animation_type = AnimationType.GLOW
                style.animation_duration = 3000.0
                style.z_index = 5
            
            # Angle-specific adjustments
            if angle_name in ["MC", "IC"]:  # Meridian angles more prominent
                style.line_width *= 1.1
                style.z_index += 1
            
            # Framework-specific adjustments
            self._apply_framework_styling(style, framework)
            
            return style
            
        except Exception as e:
            self.logger.error(f"Failed to generate aspect styling: {e}")
            return StyleMetadata()
    
    def generate_interactive_metadata(
        self,
        line_type: str,
        planet_name: str,
        additional_data: Optional[Dict[str, Any]] = None,
        framework: VisualizationFramework = VisualizationFramework.GENERIC
    ) -> InteractiveMetadata:
        """
        Generate interactive behavior metadata for ACG lines.
        
        Args:
            line_type: Type of line (MC, ASC, aspect, etc.)
            planet_name: Name of associated planet
            additional_data: Additional data for interactions
            framework: Target visualization framework
            
        Returns:
            InteractiveMetadata with interaction specifications
        """
        try:
            # Base interactive metadata
            interactive = InteractiveMetadata(
                tooltip_enabled=True,
                tooltip_template="acg_line",
                on_click_action="select",
                on_hover_action="highlight"
            )
            
            # Tooltip data
            tooltip_data = {
                "planet": planet_name,
                "line_type": line_type,
                "description": self._get_line_description(line_type, planet_name)
            }
            
            if additional_data:
                tooltip_data.update(additional_data)
            
            interactive.tooltip_data = tooltip_data
            
            # Line type specific interactions
            if line_type in ["MC", "IC", "ASC", "DSC"]:
                interactive.selection_group = "angular_lines"
                interactive.context_menu_enabled = True
                interactive.context_menu_items = [
                    {"label": "Show Planet Info", "action": "planet_info"},
                    {"label": "Hide Line", "action": "hide_line"},
                    {"label": "Adjust Styling", "action": "styling_panel"}
                ]
            
            elif "aspect" in line_type.lower():
                interactive.selection_group = "aspect_lines"
                interactive.context_menu_items = [
                    {"label": "Aspect Details", "action": "aspect_info"},
                    {"label": "Show Orb Range", "action": "show_orb"},
                    {"label": "Hide Aspect Lines", "action": "hide_aspects"}
                ]
            
            # Accessibility
            interactive.aria_label = f"{planet_name} {line_type} line"
            interactive.aria_description = self._get_line_description(line_type, planet_name)
            
            return interactive
            
        except Exception as e:
            self.logger.error(f"Failed to generate interactive metadata: {e}")
            return InteractiveMetadata()
    
    def create_legend_metadata(
        self,
        active_filters: List[str],
        aspect_types: Optional[List[AspectType]] = None,
        color_schemes: Optional[Dict[str, str]] = None
    ) -> LegendData:
        """
        Create comprehensive legend metadata for visualization.
        
        Args:
            active_filters: Currently active motion filters
            aspect_types: Active aspect types
            color_schemes: Color schemes in use
            
        Returns:
            LegendData with complete legend information
        """
        try:
            legend = LegendData(title="ACG Lines & Motion")
            
            # Add motion legend if motion filters active
            if active_filters and any(f in ["direct", "retrograde", "stationary"] for f in active_filters):
                motion_colors = color_schemes or self.COLOR_SCHEMES["motion_default"]
                legend.add_motion_legend(active_filters, motion_colors)
            
            # Add aspect legend if aspect types provided
            if aspect_types:
                aspect_colors = self.COLOR_SCHEMES["aspects_traditional"]
                legend.add_aspect_legend(aspect_types, aspect_colors)
            
            # Add general ACG line types
            if not legend.items:  # If no specific items added, add general items
                legend.items.extend([
                    {
                        "label": "MC Lines",
                        "color": "#3366cc",
                        "line_style": "solid",
                        "description": "Midheaven - career and public image",
                        "category": "angular"
                    },
                    {
                        "label": "ASC Lines", 
                        "color": "#cc6633",
                        "line_style": "solid",
                        "description": "Ascendant - personality and appearance",
                        "category": "angular"
                    }
                ])
            
            return legend
            
        except Exception as e:
            self.logger.error(f"Failed to create legend metadata: {e}")
            return LegendData()
    
    def _apply_framework_styling(
        self,
        style: StyleMetadata,
        framework: VisualizationFramework
    ) -> None:
        """Apply framework-specific styling adjustments."""
        try:
            if framework == VisualizationFramework.THREE_JS:
                # Three.js specific optimizations
                style.render_order = style.z_index
                if style.glow_effect:
                    style.animation_easing = "linear"  # Better for WebGL
            
            elif framework == VisualizationFramework.D3_JS:
                # D3.js specific optimizations
                if style.line_style == "dashed":
                    style.line_width = max(1.0, style.line_width)  # Minimum for visibility
            
            elif framework == VisualizationFramework.LEAFLET:
                # Leaflet specific optimizations
                style.line_width = max(1.0, min(8.0, style.line_width))  # Clamp to reasonable range
                
        except Exception as e:
            self.logger.error(f"Failed to apply framework styling: {e}")
    
    def _get_line_description(self, line_type: str, planet_name: str) -> str:
        """Get descriptive text for ACG lines."""
        descriptions = {
            "MC": f"Where {planet_name} would be at the Midheaven (highest point in sky)",
            "IC": f"Where {planet_name} would be at the Imum Coeli (lowest point)",
            "ASC": f"Where {planet_name} would be rising on the eastern horizon",
            "DSC": f"Where {planet_name} would be setting on the western horizon"
        }
        
        if "aspect" in line_type.lower():
            return f"Where {planet_name} forms a {line_type.replace('_', ' ')} aspect to local angles"
        
        return descriptions.get(line_type, f"{planet_name} {line_type} line")


class FrameworkRenderer:
    """
    Framework-specific rendering optimization and metadata generation.
    
    Provides optimized metadata for different visualization frameworks
    with performance considerations and best practices.
    """
    
    def __init__(self, framework: VisualizationFramework):
        self.framework = framework
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def optimize_for_three_js(self, features: List[Any]) -> Dict[str, Any]:
        """Optimize ACG features for Three.js rendering."""
        try:
            optimizations = {
                "buffer_geometry": True,
                "instance_rendering": len(features) > 100,
                "level_of_detail": len(features) > 500,
                "material_merging": True,
                "frustum_culling": True
            }
            
            # Group features by material properties for batching
            material_groups = {}
            for feature in features:
                material_key = self._get_material_key(feature)
                if material_key not in material_groups:
                    material_groups[material_key] = []
                material_groups[material_key].append(feature)
            
            return {
                "optimizations": optimizations,
                "material_groups": material_groups,
                "recommended_settings": {
                    "antialias": True,
                    "alpha": True,
                    "premultipliedAlpha": True,
                    "preserveDrawingBuffer": False
                }
            }
            
        except Exception as e:
            self.logger.error(f"Three.js optimization failed: {e}")
            return {}
    
    def optimize_for_d3_js(self, features: List[Any]) -> Dict[str, Any]:
        """Optimize ACG features for D3.js rendering."""
        try:
            return {
                "svg_optimization": {
                    "use_paths": True,
                    "simplify_curves": len(features) > 200,
                    "group_elements": True,
                    "css_styling": True
                },
                "performance_hints": {
                    "debounce_interactions": 100,  # ms
                    "lazy_render_offscreen": True,
                    "use_canvas_fallback": len(features) > 1000
                }
            }
            
        except Exception as e:
            self.logger.error(f"D3.js optimization failed: {e}")
            return {}
    
    def optimize_for_leaflet(self, features: List[Any]) -> Dict[str, Any]:
        """Optimize ACG features for Leaflet rendering."""
        try:
            return {
                "leaflet_options": {
                    "prefer_canvas": len(features) > 300,
                    "use_clustering": len(features) > 500,
                    "tile_layer_optimization": True
                },
                "layer_management": {
                    "feature_groups": True,
                    "layer_control": True,
                    "zoom_based_styling": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Leaflet optimization failed: {e}")
            return {}
    
    def _get_material_key(self, feature: Any) -> str:
        """Generate material grouping key for batching."""
        try:
            # Extract styling properties for grouping
            if hasattr(feature, 'properties'):
                props = feature.properties
                return f"{props.get('color', '#000')}_{props.get('opacity', 1.0)}_{props.get('line_style', 'solid')}"
            return "default"
        except:
            return "default"


# Global visualization metadata generator
visualization_generator = VisualizationMetadataGenerator()