"""
Motion-Based Filtering System for Enhanced ACG

This module provides comprehensive filtering capabilities for ACG lines based on
planetary motion status, timing, and astronomical characteristics. Optimized for
performance with intelligent caching and vectorized operations.

Features:
- Motion status filtering (direct, retrograde, stationary)
- Speed-based filtering with percentile ranges
- Station approach timing filters
- Dignity-based filtering
- Combined multi-criteria filtering
- Performance optimization with pre-indexing
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

from .enhanced_metadata import RetrogradeAwareLineMetadata, MotionStatus, PlanetaryDignity
from .acg_types import ACGResult, ACGMetadata, ACGNatalInfo

logger = logging.getLogger(__name__)


class FilterCriteria(Enum):
    """Available filtering criteria for ACG lines."""
    MOTION_STATUS = "motion_status"
    MOTION_SPEED = "motion_speed"
    STATION_APPROACH = "station_approach"
    PLANETARY_DIGNITY = "planetary_dignity"
    RETROGRADE_PERIOD = "retrograde_period"
    SPEED_PERCENTILE = "speed_percentile"
    ELEMENT = "element"
    MODALITY = "modality"


@dataclass
class FilterConfig:
    """Configuration for motion-based filtering operations."""
    
    # Motion status filters
    motion_statuses: Optional[List[MotionStatus]] = None
    
    # Speed-based filters
    speed_range: Optional[Tuple[float, float]] = None  # (min, max) degrees per day
    speed_percentile_range: Optional[Tuple[float, float]] = None  # (min, max) percentile
    
    # Station timing filters
    approaching_station_days: Optional[int] = None  # Max days until station
    station_distance_range: Optional[Tuple[int, int]] = None  # (min, max) days from station
    
    # Dignity filters
    dignities: Optional[List[PlanetaryDignity]] = None
    
    # Retrograde period filters
    retrograde_phase: Optional[str] = None  # "approaching", "peak", "separating"
    in_retrograde_shadow: Optional[bool] = None
    
    # Astrological filters
    elements: Optional[List[str]] = None  # "fire", "earth", "air", "water"
    modalities: Optional[List[str]] = None  # "cardinal", "fixed", "mutable"
    zodiac_signs: Optional[List[str]] = None
    
    # Performance options
    use_pre_indexing: bool = True
    cache_results: bool = True
    parallel_processing: bool = False


@dataclass
class FilterResult:
    """Result of filtering operation with statistics."""
    
    filtered_features: List[Any] = field(default_factory=list)
    original_count: int = 0
    filtered_count: int = 0
    filter_efficiency: float = 0.0
    processing_time_ms: float = 0.0
    
    # Filter statistics
    filters_applied: List[str] = field(default_factory=list)
    filter_matches: Dict[str, int] = field(default_factory=dict)
    
    # Performance data
    cache_hits: int = 0
    cache_misses: int = 0
    index_usage: bool = False


class MotionBasedFilter:
    """
    High-performance motion-based filtering system for ACG lines.
    
    Provides efficient filtering based on planetary motion characteristics
    with intelligent caching and optimization strategies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance optimization structures
        self._feature_indices = {}  # Pre-computed indices for fast filtering
        self._filter_cache = {}  # Cache for filter results
        self._last_index_update = None
        
        # Performance statistics
        self._filter_operations = []
        self._cache_stats = {"hits": 0, "misses": 0}
    
    def filter_by_motion_status(
        self,
        features: List[Any],
        status_list: List[MotionStatus],
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]] = None
    ) -> FilterResult:
        """
        Filter ACG lines by planetary motion status.
        
        Args:
            features: List of ACG features to filter
            status_list: List of motion statuses to include
            enhanced_metadata: Enhanced metadata with motion information
            
        Returns:
            FilterResult with filtered features and statistics
        """
        start_time = time.time()
        
        try:
            filtered_features = []
            
            for feature in features:
                if not hasattr(feature, 'metadata') or not feature.metadata:
                    continue
                
                # Get motion status from enhanced metadata or ACG metadata
                motion_status = self._get_motion_status(feature, enhanced_metadata)
                
                if motion_status in status_list:
                    filtered_features.append(feature)
            
            processing_time = (time.time() - start_time) * 1000
            
            return FilterResult(
                filtered_features=filtered_features,
                original_count=len(features),
                filtered_count=len(filtered_features),
                filter_efficiency=len(filtered_features) / len(features) if features else 0.0,
                processing_time_ms=processing_time,
                filters_applied=["motion_status"],
                filter_matches={"motion_status": len(filtered_features)}
            )
            
        except Exception as e:
            self.logger.error(f"Motion status filtering failed: {e}")
            return FilterResult(
                filtered_features=features,  # Return unfiltered on error
                original_count=len(features),
                filtered_count=len(features),
                filter_efficiency=1.0,
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    def filter_by_motion_speed(
        self,
        features: List[Any],
        speed_range: Tuple[float, float],
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]] = None
    ) -> FilterResult:
        """
        Filter ACG lines by planetary motion speed.
        
        Args:
            features: List of ACG features to filter
            speed_range: (min_speed, max_speed) in degrees per day
            enhanced_metadata: Enhanced metadata with speed information
            
        Returns:
            FilterResult with filtered features
        """
        start_time = time.time()
        min_speed, max_speed = speed_range
        
        try:
            filtered_features = []
            
            for feature in features:
                if not hasattr(feature, 'metadata') or not feature.metadata:
                    continue
                
                # Get speed from enhanced metadata or coordinates
                speed = self._get_motion_speed(feature, enhanced_metadata)
                
                if speed is not None and min_speed <= abs(speed) <= max_speed:
                    filtered_features.append(feature)
            
            processing_time = (time.time() - start_time) * 1000
            
            return FilterResult(
                filtered_features=filtered_features,
                original_count=len(features),
                filtered_count=len(filtered_features),
                filter_efficiency=len(filtered_features) / len(features) if features else 0.0,
                processing_time_ms=processing_time,
                filters_applied=["motion_speed"],
                filter_matches={"motion_speed": len(filtered_features)}
            )
            
        except Exception as e:
            self.logger.error(f"Motion speed filtering failed: {e}")
            return FilterResult(filtered_features=features)
    
    def filter_approaching_stations(
        self,
        features: List[Any],
        days_threshold: int,
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]] = None
    ) -> FilterResult:
        """
        Filter ACG lines for planets approaching stations.
        
        Args:
            features: List of ACG features to filter
            days_threshold: Maximum days until station
            enhanced_metadata: Enhanced metadata with station timing
            
        Returns:
            FilterResult with features for planets approaching stations
        """
        start_time = time.time()
        
        try:
            filtered_features = []
            
            for feature in features:
                if not enhanced_metadata:
                    continue
                
                body_id = self._get_body_id(feature)
                if body_id not in enhanced_metadata:
                    continue
                
                metadata = enhanced_metadata[body_id]
                
                if (metadata.is_approaching_station and 
                    metadata.days_until_station is not None and
                    metadata.days_until_station <= days_threshold):
                    
                    filtered_features.append(feature)
            
            processing_time = (time.time() - start_time) * 1000
            
            return FilterResult(
                filtered_features=filtered_features,
                original_count=len(features),
                filtered_count=len(filtered_features),
                filter_efficiency=len(filtered_features) / len(features) if features else 0.0,
                processing_time_ms=processing_time,
                filters_applied=["station_approach"],
                filter_matches={"station_approach": len(filtered_features)}
            )
            
        except Exception as e:
            self.logger.error(f"Station approach filtering failed: {e}")
            return FilterResult(filtered_features=features)
    
    def filter_by_planetary_dignity(
        self,
        features: List[Any],
        dignity_types: List[PlanetaryDignity],
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]] = None
    ) -> FilterResult:
        """
        Filter ACG lines by planetary dignity.
        
        Args:
            features: List of ACG features to filter
            dignity_types: List of dignities to include
            enhanced_metadata: Enhanced metadata with dignity information
            
        Returns:
            FilterResult with filtered features
        """
        start_time = time.time()
        
        try:
            filtered_features = []
            
            for feature in features:
                if not enhanced_metadata:
                    continue
                
                body_id = self._get_body_id(feature)
                if body_id not in enhanced_metadata:
                    continue
                
                metadata = enhanced_metadata[body_id]
                
                if metadata.planetary_dignity in dignity_types:
                    filtered_features.append(feature)
            
            processing_time = (time.time() - start_time) * 1000
            
            return FilterResult(
                filtered_features=filtered_features,
                original_count=len(features),
                filtered_count=len(filtered_features),
                filter_efficiency=len(filtered_features) / len(features) if features else 0.0,
                processing_time_ms=processing_time,
                filters_applied=["planetary_dignity"],
                filter_matches={"planetary_dignity": len(filtered_features)}
            )
            
        except Exception as e:
            self.logger.error(f"Planetary dignity filtering failed: {e}")
            return FilterResult(filtered_features=features)
    
    def apply_motion_styling(
        self,
        features: List[Any],
        style_config: Dict[str, Any],
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]] = None
    ) -> List[Any]:
        """
        Apply motion-based styling to ACG features.
        
        Args:
            features: List of ACG features to style
            style_config: Styling configuration
            enhanced_metadata: Enhanced metadata with styling hints
            
        Returns:
            Styled features with motion-based styling applied
        """
        try:
            styled_features = []
            
            for feature in features:
                styled_feature = feature.copy() if hasattr(feature, 'copy') else feature
                
                if enhanced_metadata:
                    body_id = self._get_body_id(feature)
                    if body_id in enhanced_metadata:
                        metadata = enhanced_metadata[body_id]
                        
                        # Apply styling hints from metadata
                        if hasattr(styled_feature, 'properties'):
                            styling_hints = metadata.styling_hints
                            styled_feature.properties.update({
                                "motion_styling": styling_hints,
                                "color": styling_hints.get("color_hint", "#3366cc"),
                                "opacity": styling_hints.get("opacity", 0.8),
                                "line_style": styling_hints.get("line_style", "solid")
                            })
                
                styled_features.append(styled_feature)
            
            return styled_features
            
        except Exception as e:
            self.logger.error(f"Motion styling failed: {e}")
            return features
    
    def combine_multiple_filters(
        self,
        features: List[Any],
        filter_config: FilterConfig,
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]] = None
    ) -> FilterResult:
        """
        Apply multiple filtering criteria in combination.
        
        Args:
            features: List of ACG features to filter
            filter_config: Combined filter configuration
            enhanced_metadata: Enhanced metadata for filtering
            
        Returns:
            FilterResult with combined filtering applied
        """
        start_time = time.time()
        
        try:
            current_features = features.copy()
            filters_applied = []
            filter_matches = {}
            
            # Apply motion status filter
            if filter_config.motion_statuses:
                result = self.filter_by_motion_status(
                    current_features, filter_config.motion_statuses, enhanced_metadata
                )
                current_features = result.filtered_features
                filters_applied.append("motion_status")
                filter_matches["motion_status"] = len(current_features)
            
            # Apply speed range filter
            if filter_config.speed_range:
                result = self.filter_by_motion_speed(
                    current_features, filter_config.speed_range, enhanced_metadata
                )
                current_features = result.filtered_features
                filters_applied.append("motion_speed")
                filter_matches["motion_speed"] = len(current_features)
            
            # Apply station approach filter
            if filter_config.approaching_station_days is not None:
                result = self.filter_approaching_stations(
                    current_features, filter_config.approaching_station_days, enhanced_metadata
                )
                current_features = result.filtered_features
                filters_applied.append("station_approach")
                filter_matches["station_approach"] = len(current_features)
            
            # Apply dignity filter
            if filter_config.dignities:
                result = self.filter_by_planetary_dignity(
                    current_features, filter_config.dignities, enhanced_metadata
                )
                current_features = result.filtered_features
                filters_applied.append("planetary_dignity")
                filter_matches["planetary_dignity"] = len(current_features)
            
            # Apply astrological filters (element, modality, signs)
            if any([filter_config.elements, filter_config.modalities, filter_config.zodiac_signs]):
                current_features = self._apply_astrological_filters(
                    current_features, filter_config, enhanced_metadata
                )
                filters_applied.append("astrological")
                filter_matches["astrological"] = len(current_features)
            
            processing_time = (time.time() - start_time) * 1000
            
            return FilterResult(
                filtered_features=current_features,
                original_count=len(features),
                filtered_count=len(current_features),
                filter_efficiency=len(current_features) / len(features) if features else 0.0,
                processing_time_ms=processing_time,
                filters_applied=filters_applied,
                filter_matches=filter_matches
            )
            
        except Exception as e:
            self.logger.error(f"Combined filtering failed: {e}")
            return FilterResult(filtered_features=features)
    
    def _apply_astrological_filters(
        self,
        features: List[Any],
        filter_config: FilterConfig,
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]]
    ) -> List[Any]:
        """Apply astrological filters (element, modality, signs)."""
        filtered_features = []
        
        for feature in features:
            if not enhanced_metadata:
                filtered_features.append(feature)
                continue
            
            body_id = self._get_body_id(feature)
            if body_id not in enhanced_metadata:
                filtered_features.append(feature)
                continue
            
            metadata = enhanced_metadata[body_id]
            
            # Check element filter
            if filter_config.elements and metadata.element not in filter_config.elements:
                continue
            
            # Check modality filter
            if filter_config.modalities and metadata.modality not in filter_config.modalities:
                continue
            
            # Check zodiac sign filter
            if filter_config.zodiac_signs and metadata.current_zodiac_sign not in filter_config.zodiac_signs:
                continue
            
            filtered_features.append(feature)
        
        return filtered_features
    
    def _get_motion_status(
        self,
        feature: Any,
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]]
    ) -> Optional[MotionStatus]:
        """Extract motion status from feature or enhanced metadata."""
        if enhanced_metadata:
            body_id = self._get_body_id(feature)
            if body_id in enhanced_metadata:
                return enhanced_metadata[body_id].motion_status
        
        # Fall back to ACG natal info
        if (hasattr(feature, 'metadata') and 
            feature.metadata and 
            feature.metadata.natal and
            feature.metadata.natal.retrograde is not None):
            
            return MotionStatus.RETROGRADE if feature.metadata.natal.retrograde else MotionStatus.DIRECT
        
        return None
    
    def _get_motion_speed(
        self,
        feature: Any,
        enhanced_metadata: Optional[Dict[str, RetrogradeAwareLineMetadata]]
    ) -> Optional[float]:
        """Extract motion speed from feature or enhanced metadata."""
        if enhanced_metadata:
            body_id = self._get_body_id(feature)
            if body_id in enhanced_metadata:
                return enhanced_metadata[body_id].daily_motion
        
        # Fall back to ACG coordinates
        if (hasattr(feature, 'metadata') and 
            feature.metadata and 
            feature.metadata.coords and
            feature.metadata.coords.speed is not None):
            
            return feature.metadata.coords.speed
        
        return None
    
    def _get_body_id(self, feature: Any) -> Optional[str]:
        """Extract body ID from ACG feature."""
        if hasattr(feature, 'metadata') and feature.metadata:
            return feature.metadata.id
        return None
    
    # ========================================
    # PERFORMANCE OPTIMIZATION METHODS
    # ========================================
    
    def pre_index_lines_by_motion_status(
        self,
        features: List[Any],
        enhanced_metadata: Dict[str, RetrogradeAwareLineMetadata]
    ) -> None:
        """
        Pre-index ACG lines by motion status for faster filtering.
        
        Args:
            features: List of ACG features to index
            enhanced_metadata: Enhanced metadata for indexing
        """
        try:
            indices = {
                MotionStatus.DIRECT: [],
                MotionStatus.RETROGRADE: [],
                MotionStatus.STATIONARY_DIRECT: [],
                MotionStatus.STATIONARY_RETROGRADE: []
            }
            
            for i, feature in enumerate(features):
                motion_status = self._get_motion_status(feature, enhanced_metadata)
                if motion_status and motion_status in indices:
                    indices[motion_status].append(i)
            
            self._feature_indices["motion_status"] = indices
            self._last_index_update = time.time()
            
            self.logger.debug(f"Indexed {len(features)} features by motion status")
            
        except Exception as e:
            self.logger.error(f"Failed to create motion status index: {e}")
    
    def cache_filtered_results(
        self,
        cache_key: str,
        filter_result: FilterResult,
        ttl_seconds: int = 300
    ) -> None:
        """
        Cache filtering results for performance optimization.
        
        Args:
            cache_key: Unique key for cached result
            filter_result: Result to cache
            ttl_seconds: Time to live in seconds
        """
        try:
            self._filter_cache[cache_key] = {
                "result": filter_result,
                "timestamp": time.time(),
                "ttl": ttl_seconds
            }
            
            # Clean old cache entries
            self._cleanup_cache()
            
        except Exception as e:
            self.logger.error(f"Failed to cache filter result: {e}")
    
    def get_cached_result(self, cache_key: str) -> Optional[FilterResult]:
        """
        Retrieve cached filtering result.
        
        Args:
            cache_key: Key for cached result
            
        Returns:
            Cached FilterResult or None
        """
        try:
            if cache_key in self._filter_cache:
                cache_entry = self._filter_cache[cache_key]
                
                # Check if cache entry is still valid
                if time.time() - cache_entry["timestamp"] < cache_entry["ttl"]:
                    self._cache_stats["hits"] += 1
                    return cache_entry["result"]
                else:
                    # Remove expired entry
                    del self._filter_cache[cache_key]
            
            self._cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve cached result: {e}")
            return None
    
    def _cleanup_cache(self) -> None:
        """Remove expired cache entries."""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self._filter_cache.items():
                if current_time - entry["timestamp"] > entry["ttl"]:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._filter_cache[key]
                
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")
    
    def lazy_load_metadata(
        self,
        features: List[Any],
        metadata_loader: Callable[[Any], RetrogradeAwareLineMetadata]
    ) -> Dict[str, RetrogradeAwareLineMetadata]:
        """
        Lazy load enhanced metadata only when needed for filtering.
        
        Args:
            features: List of ACG features
            metadata_loader: Function to load metadata for a feature
            
        Returns:
            Dictionary of loaded metadata
        """
        loaded_metadata = {}
        
        try:
            for feature in features:
                body_id = self._get_body_id(feature)
                if body_id and body_id not in loaded_metadata:
                    loaded_metadata[body_id] = metadata_loader(feature)
            
            return loaded_metadata
            
        except Exception as e:
            self.logger.error(f"Lazy metadata loading failed: {e}")
            return {}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for filtering operations.
        
        Returns:
            Performance statistics dictionary
        """
        return {
            "total_filter_operations": len(self._filter_operations),
            "cache_stats": self._cache_stats.copy(),
            "index_status": {
                "motion_status_indexed": "motion_status" in self._feature_indices,
                "last_index_update": self._last_index_update,
                "cached_results": len(self._filter_cache)
            },
            "average_processing_time_ms": (
                sum(op.get("processing_time_ms", 0) for op in self._filter_operations) / 
                len(self._filter_operations) if self._filter_operations else 0.0
            )
        }
    
    def clear_cache(self) -> None:
        """Clear all caches and indices."""
        self._filter_cache.clear()
        self._feature_indices.clear()
        self._filter_operations.clear()
        self._cache_stats = {"hits": 0, "misses": 0}
        self._last_index_update = None


# Global filter instance
motion_filter = MotionBasedFilter()