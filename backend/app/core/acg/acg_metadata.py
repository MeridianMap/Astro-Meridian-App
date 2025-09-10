"""
ACG Metadata & Provenance Handling (PRP 5)

Implements robust metadata and provenance handling for all ACG outputs.
Ensures every feature includes complete, standards-compliant metadata,
and that provenance (calculation source, version, flags, etc.) is always
attached and queryable.

This module provides:
- Metadata schema validation and enforcement
- Provenance tracking and attachment
- Metadata enrichment and standardization
- Schema validation and compliance checking
- Queryable metadata and provenance APIs
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import logging
import json
from dataclasses import asdict

from .acg_types import (
    ACGMetadata, ACGCoordinates, ACGLineInfo, ACGNatalInfo, 
    ACGBodyType, ACGResult, ACGLineData
)
from .acg_utils import get_swiss_ephemeris_version

logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class ACGMetadataManager:
    """
    Manages metadata and provenance for ACG calculations.
    
    Ensures all ACG outputs include complete, standards-compliant metadata
    and maintains comprehensive provenance tracking.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metadata_schema_version = "1.0.0"
        
        # Required metadata fields according to master context
        self.required_fields = {
            'id', 'type', 'kind', 'epoch', 'jd', 'gmst', 'obliquity',
            'coords', 'line', 'source', 'calculation_time_ms'
        }
        
        # Optional metadata fields
        self.optional_fields = {
            'number', 'natal', 'flags', 'se_version', 'color', 'style',
            'z_index', 'hit_radius', 'custom'
        }
        
        # Provenance tracking
        self.provenance_info = {
            'system': 'Meridian-ACG',
            'version': self.metadata_schema_version,
            'se_version': get_swiss_ephemeris_version(),
            'created': datetime.utcnow().isoformat() + 'Z'
        }
    
    def create_base_metadata(
        self,
        body_id: str,
        body_type: ACGBodyType,
        epoch: str,
        jd: float,
        gmst: float,
        obliquity: float,
        coordinates: ACGCoordinates,
        calculation_time_ms: float,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create base metadata template for ACG features.
        
        Args:
            body_id: Body identifier
            body_type: Body type enum
            epoch: ISO UTC timestamp
            jd: Julian Day
            gmst: Greenwich Mean Sidereal Time
            obliquity: True obliquity in degrees
            coordinates: Celestial coordinates
            calculation_time_ms: Calculation time
            **kwargs: Additional metadata fields
            
        Returns:
            Base metadata dictionary
        """
        base_metadata = {
            'id': body_id,
            'type': 'body',
            'kind': body_type,
            'epoch': epoch,
            'jd': jd,
            'gmst': gmst,
            'obliquity': obliquity,
            'coords': coordinates,
            'source': 'Meridian-ACG',
            'calculation_time_ms': calculation_time_ms,
            'se_version': get_swiss_ephemeris_version(),
            'schema_version': self.metadata_schema_version,
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Add optional fields from kwargs
        for field in self.optional_fields:
            if field in kwargs and kwargs[field] is not None:
                base_metadata[field] = kwargs[field]
        
        return base_metadata
    
    def create_line_metadata(
        self,
        base_metadata: Dict[str, Any],
        line_info: ACGLineInfo,
        natal_info: Optional[ACGNatalInfo] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> ACGMetadata:
        """
        Create complete line metadata from base metadata and line info.
        
        Args:
            base_metadata: Base metadata dictionary
            line_info: Line-specific information
            natal_info: Optional natal chart context
            custom_fields: Optional custom metadata fields
            
        Returns:
            Complete ACGMetadata object
            
        Raises:
            ValueError: If required fields are missing
        """
        try:
            # Validate required fields
            self._validate_required_fields(base_metadata)
            
            # Create ACGMetadata object
            metadata = ACGMetadata(
                id=base_metadata['id'],
                type=base_metadata['type'],
                kind=base_metadata['kind'],
                epoch=base_metadata['epoch'],
                jd=base_metadata['jd'],
                gmst=base_metadata['gmst'],
                obliquity=base_metadata['obliquity'],
                coords=base_metadata['coords'],
                line=line_info,
                calculation_time_ms=base_metadata['calculation_time_ms'],
                number=base_metadata.get('number'),
                natal=natal_info,
                flags=base_metadata.get('flags'),
                se_version=base_metadata.get('se_version'),
                source=base_metadata.get('source', 'Meridian-ACG'),
                color=base_metadata.get('color'),
                style=base_metadata.get('style'),
                z_index=base_metadata.get('z_index'),
                hit_radius=base_metadata.get('hit_radius'),
                custom=custom_fields
            )
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to create line metadata: {e}")
            raise ValueError(f"Metadata creation failed: {e}")
    
    def _validate_required_fields(self, metadata: Dict[str, Any]) -> None:
        """
        Validate that all required metadata fields are present.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = []
        for field in self.required_fields:
            if field == 'line':
                continue  # Line info is handled separately
            if field not in metadata:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required metadata fields: {missing_fields}")
    
    def validate_metadata_completeness(self, metadata: ACGMetadata) -> Dict[str, Any]:
        """
        Validate metadata completeness and correctness.
        
        Args:
            metadata: ACG metadata to validate
            
        Returns:
            Validation result with status and details
        """
        result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'completeness_score': 0.0
        }
        
        try:
            # Check required fields
            metadata_dict = asdict(metadata)
            missing_required = []
            
            for field in self.required_fields:
                if field not in metadata_dict or metadata_dict[field] is None:
                    missing_required.append(field)
            
            if missing_required:
                result['errors'].append(f"Missing required fields: {missing_required}")
                result['valid'] = False
            
            # Check field validity
            validation_checks = [
                ('id', lambda x: isinstance(x, str) and len(x) > 0),
                ('jd', lambda x: isinstance(x, (int, float)) and x > 0),
                ('gmst', lambda x: isinstance(x, (int, float)) and 0 <= x <= 360),
                ('obliquity', lambda x: isinstance(x, (int, float)) and -90 <= x <= 90),
                ('calculation_time_ms', lambda x: isinstance(x, (int, float)) and x >= 0)
            ]
            
            for field_name, validator in validation_checks:
                if hasattr(metadata, field_name):
                    field_value = getattr(metadata, field_name)
                    if field_value is not None and not validator(field_value):
                        result['errors'].append(f"Invalid {field_name}: {field_value}")
                        result['valid'] = False
            
            # Check coordinates validity
            if metadata.coords:
                coord_checks = [
                    ('lambda_', lambda x: 0 <= x <= 360),
                    ('beta', lambda x: -90 <= x <= 90),
                    ('ra', lambda x: 0 <= x <= 360),
                    ('dec', lambda x: -90 <= x <= 90)
                ]
                
                for coord_field, validator in coord_checks:
                    if hasattr(metadata.coords, coord_field):
                        coord_value = getattr(metadata.coords, coord_field)
                        if coord_value is not None and not validator(coord_value):
                            result['errors'].append(f"Invalid coordinate {coord_field}: {coord_value}")
                            result['valid'] = False
            
            # Calculate completeness score with weighting:
            # 80% weight on required fields, 20% on optional fields
            required_total = len(self.required_fields)
            optional_total = len(self.optional_fields)
            required_present = sum(1 for field in self.required_fields
                                   if hasattr(metadata, field) and getattr(metadata, field) is not None)
            optional_present = sum(1 for field in self.optional_fields
                                   if hasattr(metadata, field) and getattr(metadata, field) is not None)

            req_score = (required_present / required_total) if required_total else 1.0
            opt_score = (optional_present / optional_total) if optional_total else 1.0
            result['completeness_score'] = 0.8 * req_score + 0.2 * opt_score
            
            # Add warnings for missing optional fields
            if result['completeness_score'] < 0.8:
                result['warnings'].append("Metadata completeness below 80%")
            
            if not metadata.natal:
                result['warnings'].append("No natal context available")
            
            if not metadata.se_version:
                result['warnings'].append("Swiss Ephemeris version not recorded")
            
        except Exception as e:
            result['errors'].append(f"Validation error: {e}")
            result['valid'] = False
        
        return result
    
    def enrich_metadata_with_provenance(
        self,
        metadata: ACGMetadata,
        calculation_context: Optional[Dict[str, Any]] = None
    ) -> ACGMetadata:
        """
        Enrich metadata with additional provenance information.
        
        Args:
            metadata: Existing metadata
            calculation_context: Additional calculation context
            
        Returns:
            Enhanced metadata with provenance
        """
        try:
            # Create enhanced custom fields
            custom_fields = metadata.custom or {}
            
            # Add provenance information
            custom_fields.update({
                'provenance': {
                    'system': 'Meridian-ACG',
                    'schema_version': self.metadata_schema_version,
                    'calculation_engine': 'ACGCalculationEngine',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            })
            
            # Add calculation context if provided
            if calculation_context:
                custom_fields['provenance']['context'] = calculation_context
            
            # Add system information
            custom_fields['system_info'] = {
                'se_version': get_swiss_ephemeris_version(),
                'metadata_manager_version': self.metadata_schema_version
            }
            
            # Create new metadata with enriched custom fields
            enhanced_metadata = ACGMetadata(
                id=metadata.id,
                type=metadata.type,
                kind=metadata.kind,
                epoch=metadata.epoch,
                jd=metadata.jd,
                gmst=metadata.gmst,
                obliquity=metadata.obliquity,
                coords=metadata.coords,
                line=metadata.line,
                calculation_time_ms=metadata.calculation_time_ms,
                number=metadata.number,
                natal=metadata.natal,
                flags=metadata.flags,
                se_version=metadata.se_version,
                source=metadata.source,
                color=metadata.color,
                style=metadata.style,
                z_index=metadata.z_index,
                hit_radius=metadata.hit_radius,
                custom=custom_fields
            )
            
            return enhanced_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to enrich metadata with provenance: {e}")
            return metadata  # Return original if enrichment fails
    
    def generate_metadata_summary(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for a collection of ACG features.
        
        Args:
            features: List of GeoJSON features with ACG metadata
            
        Returns:
            Summary statistics and metadata analysis
        """
        summary = {
            'total_features': len(features),
            'feature_types': {},
            'body_types': {},
            'line_types': {},
            'calculation_stats': {
                'total_time_ms': 0.0,
                'avg_time_ms': 0.0,
                'min_time_ms': float('inf'),
                'max_time_ms': 0.0
            },
            'provenance': {
                'sources': set(),
                'se_versions': set(),
                'epochs': set()
            },
            'completeness': {
                'with_natal': 0,
                'with_provenance': 0,
                'complete_metadata': 0
            }
        }
        
        try:
            for feature in features:
                props = feature.get('properties', {})
                
                # Count feature types
                feature_type = props.get('type', 'unknown')
                summary['feature_types'][feature_type] = summary['feature_types'].get(feature_type, 0) + 1
                
                # Count body types
                body_kind = props.get('kind', 'unknown')
                summary['body_types'][body_kind] = summary['body_types'].get(body_kind, 0) + 1
                
                # Count line types
                line_info = props.get('line', {})
                line_type = line_info.get('line_type', 'unknown')
                summary['line_types'][line_type] = summary['line_types'].get(line_type, 0) + 1
                
                # Calculation statistics
                calc_time = props.get('calculation_time_ms', 0.0)
                if calc_time > 0:
                    summary['calculation_stats']['total_time_ms'] += calc_time
                    summary['calculation_stats']['min_time_ms'] = min(
                        summary['calculation_stats']['min_time_ms'], calc_time
                    )
                    summary['calculation_stats']['max_time_ms'] = max(
                        summary['calculation_stats']['max_time_ms'], calc_time
                    )
                
                # Provenance tracking
                source = props.get('source')
                if source:
                    summary['provenance']['sources'].add(source)
                
                se_version = props.get('se_version')
                if se_version:
                    summary['provenance']['se_versions'].add(se_version)
                
                epoch = props.get('epoch')
                if epoch:
                    summary['provenance']['epochs'].add(epoch)
                
                # Completeness tracking
                if props.get('natal'):
                    summary['completeness']['with_natal'] += 1
                
                if props.get('custom', {}).get('provenance'):
                    summary['completeness']['with_provenance'] += 1
                
                # Check for complete metadata (all required fields present)
                required_present = all(
                    field in props for field in 
                    ['id', 'type', 'kind', 'epoch', 'jd', 'source']
                )
                if required_present:
                    summary['completeness']['complete_metadata'] += 1
            
            # Calculate average calculation time
            if len(features) > 0:
                summary['calculation_stats']['avg_time_ms'] = (
                    summary['calculation_stats']['total_time_ms'] / len(features)
                )
            
            # Convert sets to lists for JSON serialization
            for key in summary['provenance']:
                if isinstance(summary['provenance'][key], set):
                    summary['provenance'][key] = list(summary['provenance'][key])
            
        except Exception as e:
            self.logger.error(f"Failed to generate metadata summary: {e}")
            summary['error'] = str(e)
        
        return summary
    
    def export_metadata_schema(self) -> Dict[str, Any]:
        """
        Export the complete ACG metadata schema.
        
        Returns:
            JSON schema definition for ACG metadata
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ACG Feature Metadata Schema",
            "description": "Schema for Astrocartography feature metadata properties",
            "version": self.metadata_schema_version,
            "type": "object",
            "required": list(self.required_fields),
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Body identifier (e.g., 'Sun', 'Venus', 'Regulus')"
                },
                "type": {
                    "type": "string", 
                    "description": "Feature type (body, line, paran, etc.)"
                },
                "kind": {
                    "type": "string",
                    "enum": [t.value for t in ACGBodyType],
                    "description": "Body kind (planet, asteroid, lot, etc.)"
                },
                "number": {
                    "type": ["integer", "null"],
                    "description": "Swiss Ephemeris or internal index"
                },
                "epoch": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO UTC timestamp"
                },
                "jd": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Julian Day"
                },
                "gmst": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 360,
                    "description": "Greenwich Mean Sidereal Time in degrees"
                },
                "obliquity": {
                    "type": "number",
                    "minimum": -90,
                    "maximum": 90,
                    "description": "True obliquity in degrees"
                },
                "coords": {
                    "type": "object",
                    "required": ["ra", "dec", "lambda", "beta"],
                    "properties": {
                        "ra": {"type": "number", "minimum": 0, "maximum": 360},
                        "dec": {"type": "number", "minimum": -90, "maximum": 90},
                        "lambda": {"type": "number", "minimum": 0, "maximum": 360},
                        "beta": {"type": "number", "minimum": -90, "maximum": 90},
                        "distance": {"type": ["number", "null"]},
                        "speed": {"type": ["number", "null"]}
                    }
                },
                "line": {
                    "type": "object",
                    "required": ["angle", "line_type", "method"],
                    "properties": {
                        "angle": {"type": ["string", "number"]},
                        "aspect": {"type": ["string", "null"]},
                        "line_type": {"type": "string"},
                        "method": {"type": "string"},
                        "segment_id": {"type": ["string", "null"]},
                        "orb": {"type": ["number", "null"]}
                    }
                },
                "natal": {
                    "type": ["object", "null"],
                    "properties": {
                        "dignity": {"type": ["string", "null"]},
                        "house": {"type": ["string", "integer", "null"]},
                        "retrograde": {"type": ["boolean", "null"]},
                        "sign": {"type": ["string", "null"]},
                        "element": {"type": ["string", "null"]},
                        "modality": {"type": ["string", "null"]},
                        "aspects": {"type": ["array", "null"]}
                    }
                },
                "flags": {"type": ["integer", "null"]},
                "se_version": {"type": ["string", "null"]},
                "source": {"type": "string"},
                "calculation_time_ms": {"type": "number", "minimum": 0},
                "color": {"type": ["string", "null"]},
                "style": {"type": ["string", "null"]},
                "z_index": {"type": ["integer", "null"]},
                "hit_radius": {"type": ["number", "null"]},
                "custom": {"type": ["object", "null"]}
            },
            "additionalProperties": False
        }
        
        return schema
    
    def validate_against_schema(self, feature_properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate feature properties against the metadata schema.
        
        Args:
            feature_properties: GeoJSON feature properties to validate
            
        Returns:
            Validation result
        """
        try:
            import jsonschema
            
            schema = self.export_metadata_schema()
            jsonschema.validate(feature_properties, schema)
            
            return {'valid': True, 'errors': []}
            
        except ImportError:
            self.logger.warning("jsonschema not available for validation")
            return {'valid': True, 'errors': [], 'warning': 'Schema validation skipped'}
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
    
    def get_provenance_info(self) -> Dict[str, Any]:
        """
        Get current system provenance information.
        
        Returns:
            System provenance data
        """
        return self.provenance_info.copy()