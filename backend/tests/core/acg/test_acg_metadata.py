"""
Test Suite for ACG Metadata & Provenance Handling (PRP 5)

Comprehensive tests for metadata and provenance management including:
- Metadata schema validation and compliance
- Provenance tracking and attachment
- Metadata completeness checking
- Schema export and validation
- Metadata enrichment and standardization
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from extracted.systems.acg_engine.acg_metadata import ACGMetadataManager
from extracted.systems.acg_engine.acg_types import (
    ACGMetadata, ACGCoordinates, ACGLineInfo, ACGNatalInfo,
    ACGBodyType, ACGLineType
)


class TestACGMetadataManager:
    """Test ACG metadata manager initialization and basic functions."""
    
    @pytest.fixture
    def metadata_manager(self):
        """ACG metadata manager instance."""
        return ACGMetadataManager()
    
    @pytest.fixture
    def sample_coordinates(self):
        """Sample celestial coordinates."""
        return ACGCoordinates(
            ra=120.5,
            dec=15.2,
            lambda_=125.8,
            beta=1.1,
            distance=1.016,
            speed=0.985
        )
    
    @pytest.fixture
    def sample_line_info(self):
        """Sample line information."""
        return ACGLineInfo(
            angle="MC",
            line_type="MC",
            method="apparent, true obliquity, meridian crossing"
        )
    
    @pytest.fixture
    def sample_natal_info(self):
        """Sample natal information."""
        return ACGNatalInfo(
            dignity="ruler",
            house=10,
            retrograde=False,
            sign="Leo",
            element="Fire",
            modality="Fixed",
            aspects=[
                {"aspect_name": "trine", "other_body": "Moon", "orb": 2.5}
            ]
        )
    
    def test_metadata_manager_initialization(self, metadata_manager):
        """Test metadata manager initializes correctly."""
        assert metadata_manager is not None
        assert len(metadata_manager.required_fields) > 0
        assert len(metadata_manager.optional_fields) > 0
        assert metadata_manager.metadata_schema_version == "1.0.0"
        assert 'system' in metadata_manager.provenance_info
    
    def test_create_base_metadata(self, metadata_manager, sample_coordinates):
        """Test creating base metadata template."""
        base_metadata = metadata_manager.create_base_metadata(
            body_id="Sun",
            body_type=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.5,
            obliquity=23.4,
            coordinates=sample_coordinates,
            calculation_time_ms=15.5,
            number=0,
            flags=258
        )
        
        assert base_metadata['id'] == 'Sun'
        assert base_metadata['type'] == 'body'
        assert base_metadata['kind'] == ACGBodyType.PLANET
        assert base_metadata['jd'] == 2451545.0
        assert base_metadata['source'] == 'Meridian-ACG'
        assert base_metadata['number'] == 0
        assert base_metadata['flags'] == 258
        assert 'created_at' in base_metadata
    
    def test_create_line_metadata_complete(
        self, 
        metadata_manager, 
        sample_coordinates,
        sample_line_info,
        sample_natal_info
    ):
        """Test creating complete line metadata."""
        base_metadata = metadata_manager.create_base_metadata(
            body_id="Sun",
            body_type=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.5,
            obliquity=23.4,
            coordinates=sample_coordinates,
            calculation_time_ms=15.5
        )
        
        custom_fields = {"test_field": "test_value"}
        
        metadata = metadata_manager.create_line_metadata(
            base_metadata,
            sample_line_info,
            sample_natal_info,
            custom_fields
        )
        
        assert isinstance(metadata, ACGMetadata)
        assert metadata.id == 'Sun'
        assert metadata.line.angle == 'MC'
        assert metadata.natal.sign == 'Leo'
        assert metadata.custom == custom_fields
    
    def test_create_line_metadata_minimal(
        self,
        metadata_manager,
        sample_coordinates,
        sample_line_info
    ):
        """Test creating minimal line metadata."""
        base_metadata = metadata_manager.create_base_metadata(
            body_id="Moon",
            body_type=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.5,
            obliquity=23.4,
            coordinates=sample_coordinates,
            calculation_time_ms=12.3
        )
        
        metadata = metadata_manager.create_line_metadata(
            base_metadata,
            sample_line_info
        )
        
        assert isinstance(metadata, ACGMetadata)
        assert metadata.id == 'Moon'
        assert metadata.natal is None
        assert metadata.custom is None
    
    def test_create_line_metadata_missing_required_fields(
        self,
        metadata_manager,
        sample_line_info
    ):
        """Test creating metadata with missing required fields fails."""
        incomplete_metadata = {
            'id': 'Sun',
            'type': 'body'
            # Missing required fields: kind, epoch, jd, etc.
        }
        
        with pytest.raises(ValueError, match="Missing required metadata fields"):
            metadata_manager.create_line_metadata(
                incomplete_metadata,
                sample_line_info
            )


class TestMetadataValidation:
    """Test metadata validation and completeness checking."""
    
    @pytest.fixture
    def metadata_manager(self):
        """ACG metadata manager instance."""
        return ACGMetadataManager()
    
    @pytest.fixture
    def valid_metadata(self):
        """Valid complete metadata for testing."""
        return ACGMetadata(
            id="Sun",
            type="body",
            kind=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.5,
            obliquity=23.4,
            coords=ACGCoordinates(
                ra=120.5, dec=15.2, lambda_=125.8, beta=1.1,
                distance=1.016, speed=0.985
            ),
            line=ACGLineInfo(
                angle="MC",
                line_type="MC",
                method="apparent, true obliquity, meridian crossing"
            ),
            calculation_time_ms=15.5,
            number=0,
            se_version="2.10.03",
            source="Meridian-ACG"
        )
    
    def test_validate_metadata_completeness_valid(self, metadata_manager, valid_metadata):
        """Test validation of valid complete metadata."""
        result = metadata_manager.validate_metadata_completeness(valid_metadata)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['completeness_score'] > 0.8
        assert isinstance(result['warnings'], list)
    
    def test_validate_metadata_completeness_missing_natal(
        self, 
        metadata_manager,
        valid_metadata
    ):
        """Test validation warns about missing natal data."""
        result = metadata_manager.validate_metadata_completeness(valid_metadata)
        
        assert result['valid'] is True
        warning_messages = ' '.join(result['warnings'])
        assert 'natal context' in warning_messages.lower()
    
    def test_validate_metadata_with_invalid_coordinates(self, metadata_manager):
        """Test validation catches invalid coordinate values."""
        invalid_metadata = ACGMetadata(
            id="TestBody",
            type="body",
            kind=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.5,
            obliquity=23.4,
            coords=ACGCoordinates(
                ra=400.0,  # Invalid: > 360
                dec=95.0,  # Invalid: > 90
                lambda_=125.8,
                beta=1.1
            ),
            line=ACGLineInfo(
                angle="MC",
                line_type="MC",
                method="test"
            ),
            calculation_time_ms=15.5
        )
        
        result = metadata_manager.validate_metadata_completeness(invalid_metadata)
        
        assert result['valid'] is False
        error_messages = ' '.join(result['errors'])
        assert 'Invalid coordinate' in error_messages
    
    def test_validate_metadata_with_invalid_values(self, metadata_manager):
        """Test validation catches various invalid field values."""
        invalid_metadata = ACGMetadata(
            id="",  # Invalid: empty string
            type="body",
            kind=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=-1.0,  # Invalid: negative JD
            gmst=400.0,  # Invalid: > 360
            obliquity=100.0,  # Invalid: > 90
            coords=ACGCoordinates(ra=120.5, dec=15.2, lambda_=125.8, beta=1.1),
            line=ACGLineInfo(angle="MC", line_type="MC", method="test"),
            calculation_time_ms=-5.0  # Invalid: negative time
        )
        
        result = metadata_manager.validate_metadata_completeness(invalid_metadata)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0


class TestProvenanceHandling:
    """Test provenance tracking and enrichment."""
    
    @pytest.fixture
    def metadata_manager(self):
        """ACG metadata manager instance."""
        return ACGMetadataManager()
    
    @pytest.fixture
    def basic_metadata(self):
        """Basic metadata for provenance testing."""
        return ACGMetadata(
            id="Venus",
            type="body",
            kind=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.5,
            obliquity=23.4,
            coords=ACGCoordinates(ra=120.5, dec=15.2, lambda_=125.8, beta=1.1),
            line=ACGLineInfo(angle="AC", line_type="AC", method="horizon crossing"),
            calculation_time_ms=18.2
        )
    
    def test_enrich_metadata_with_provenance(self, metadata_manager, basic_metadata):
        """Test enriching metadata with provenance information."""
        calculation_context = {
            'request_id': 'test-123',
            'calculation_method': 'standard',
            'precision': 'high'
        }
        
        enriched = metadata_manager.enrich_metadata_with_provenance(
            basic_metadata,
            calculation_context
        )
        
        assert enriched.custom is not None
        assert 'provenance' in enriched.custom
        assert 'system_info' in enriched.custom
        
        provenance = enriched.custom['provenance']
        assert provenance['system'] == 'Meridian-ACG'
        assert 'timestamp' in provenance
        assert provenance['context'] == calculation_context
        
        system_info = enriched.custom['system_info']
        assert 'se_version' in system_info
        assert 'metadata_manager_version' in system_info
    
    def test_enrich_metadata_preserves_existing_custom_fields(
        self,
        metadata_manager,
        basic_metadata
    ):
        """Test that enrichment preserves existing custom fields."""
        # Add existing custom fields
        basic_metadata.custom = {'existing_field': 'existing_value'}
        
        enriched = metadata_manager.enrich_metadata_with_provenance(basic_metadata)
        
        assert enriched.custom is not None
        assert enriched.custom['existing_field'] == 'existing_value'
        assert 'provenance' in enriched.custom
    
    def test_get_provenance_info(self, metadata_manager):
        """Test getting system provenance information."""
        provenance = metadata_manager.get_provenance_info()
        
        assert 'system' in provenance
        assert provenance['system'] == 'Meridian-ACG'
        assert 'version' in provenance
        assert 'se_version' in provenance
        assert 'created' in provenance


class TestMetadataSummaryAndSchema:
    """Test metadata summary generation and schema export."""
    
    @pytest.fixture
    def metadata_manager(self):
        """ACG metadata manager instance."""
        return ACGMetadataManager()
    
    @pytest.fixture
    def sample_features(self):
        """Sample GeoJSON features for summary testing."""
        return [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                "properties": {
                    "id": "Sun",
                    "type": "body",
                    "kind": "planet",
                    "epoch": "2000-01-01T12:00:00Z",
                    "jd": 2451545.0,
                    "source": "Meridian-ACG",
                    "line": {"line_type": "MC"},
                    "calculation_time_ms": 15.5,
                    "se_version": "2.10.03",
                    "natal": {"sign": "Leo", "house": 10}
                }
            },
            {
                "type": "Feature", 
                "geometry": {"type": "LineString", "coordinates": [[0, 0], [2, 2]]},
                "properties": {
                    "id": "Moon",
                    "type": "body",
                    "kind": "planet",
                    "epoch": "2000-01-01T12:00:00Z",
                    "jd": 2451545.0,
                    "source": "Meridian-ACG",
                    "line": {"line_type": "IC"},
                    "calculation_time_ms": 12.3,
                    "se_version": "2.10.03",
                    "custom": {
                        "provenance": {
                            "system": "Meridian-ACG",
                            "timestamp": "2000-01-01T12:00:00Z"
                        }
                    }
                }
            }
        ]
    
    def test_generate_metadata_summary(self, metadata_manager, sample_features):
        """Test generating metadata summary for features."""
        summary = metadata_manager.generate_metadata_summary(sample_features)
        
        assert summary['total_features'] == 2
        assert 'body' in summary['feature_types']
        assert summary['feature_types']['body'] == 2
        
        assert 'planet' in summary['body_types']
        assert summary['body_types']['planet'] == 2
        
        assert 'MC' in summary['line_types']
        assert 'IC' in summary['line_types']
        
        calc_stats = summary['calculation_stats']
        assert calc_stats['total_time_ms'] == 27.8  # 15.5 + 12.3
        assert calc_stats['avg_time_ms'] == 13.9
        assert calc_stats['min_time_ms'] == 12.3
        assert calc_stats['max_time_ms'] == 15.5
        
        assert 'Meridian-ACG' in summary['provenance']['sources']
        assert '2.10.03' in summary['provenance']['se_versions']
        
        assert summary['completeness']['with_natal'] == 1
        assert summary['completeness']['with_provenance'] == 1
        assert summary['completeness']['complete_metadata'] == 2
    
    def test_generate_metadata_summary_empty_features(self, metadata_manager):
        """Test generating summary for empty feature list."""
        summary = metadata_manager.generate_metadata_summary([])
        
        assert summary['total_features'] == 0
        assert summary['calculation_stats']['avg_time_ms'] == 0.0
        assert len(summary['provenance']['sources']) == 0
    
    def test_export_metadata_schema(self, metadata_manager):
        """Test exporting metadata schema."""
        schema = metadata_manager.export_metadata_schema()
        
        assert schema['$schema'] == "http://json-schema.org/draft-07/schema#"
        assert schema['title'] == "ACG Feature Metadata Schema"
        assert schema['version'] == metadata_manager.metadata_schema_version
        assert schema['type'] == 'object'
        
        assert 'required' in schema
        assert 'properties' in schema
        
        # Check required fields are in schema
        for field in metadata_manager.required_fields:
            if field != 'line':  # 'line' is handled as nested object
                assert field in schema['properties']
        
        # Check coordinate schema
        coords_schema = schema['properties']['coords']
        assert coords_schema['type'] == 'object'
        assert 'ra' in coords_schema['properties']
        assert 'dec' in coords_schema['properties']
        
        # Check line schema
        line_schema = schema['properties']['line']
        assert line_schema['type'] == 'object'
        assert 'angle' in line_schema['properties']
        assert 'line_type' in line_schema['properties']
    
    def test_validate_against_schema(self, metadata_manager):
        """Test validating properties against schema."""
        valid_properties = {
            "id": "Sun",
            "type": "body",
            "kind": "planet",
            "epoch": "2000-01-01T12:00:00Z",
            "jd": 2451545.0,
            "gmst": 280.5,
            "obliquity": 23.4,
            "coords": {
                "ra": 120.5,
                "dec": 15.2,
                "lambda": 125.8,
                "beta": 1.1
            },
            "line": {
                "angle": "MC",
                "line_type": "MC",
                "method": "test"
            },
            "source": "Meridian-ACG",
            "calculation_time_ms": 15.5
        }
        
        result = metadata_manager.validate_against_schema(valid_properties)
        
        # Should pass even if jsonschema is not available
        assert result['valid'] is True


class TestErrorHandling:
    """Test error handling in metadata operations."""
    
    @pytest.fixture
    def metadata_manager(self):
        """ACG metadata manager instance."""
        return ACGMetadataManager()
    
    def test_create_line_metadata_with_invalid_base(self, metadata_manager):
        """Test error handling when creating metadata with invalid base."""
        invalid_base = {}  # Missing all required fields
        
        line_info = ACGLineInfo(
            angle="MC",
            line_type="MC", 
            method="test"
        )
        
        with pytest.raises(ValueError):
            metadata_manager.create_line_metadata(invalid_base, line_info)
    
    def test_enrich_metadata_with_error_recovery(self, metadata_manager):
        """Test that enrichment errors don't break the process."""
        # Create metadata with problematic custom field
        problem_metadata = ACGMetadata(
            id="TestBody",
            type="body",
            kind=ACGBodyType.PLANET,
            epoch="2000-01-01T12:00:00Z",
            jd=2451545.0,
            gmst=280.5,
            obliquity=23.4,
            coords=ACGCoordinates(ra=120.5, dec=15.2, lambda_=125.8, beta=1.1),
            line=ACGLineInfo(angle="MC", line_type="MC", method="test"),
            calculation_time_ms=15.5
        )
        
        # Should not raise exception, returns original metadata
        enriched = metadata_manager.enrich_metadata_with_provenance(problem_metadata)
        assert enriched is not None
        assert enriched.id == "TestBody"
    
    def test_generate_summary_with_malformed_features(self, metadata_manager):
        """Test summary generation handles malformed features gracefully."""
        malformed_features = [
            {"type": "Feature"},  # Missing properties
            {"properties": {}},   # Missing type
            {"properties": {"calculation_time_ms": "invalid"}},  # Invalid data type
        ]
        
        summary = metadata_manager.generate_metadata_summary(malformed_features)
        
        assert summary['total_features'] == 3
        assert 'unknown' in summary['feature_types']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])