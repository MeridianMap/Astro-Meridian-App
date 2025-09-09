"""
Test suite for essential dignities calculation fixes.

Validates the remediation of critical calculation errors identified in the review:
- Sun in Gemini incorrectly showing exaltation and triplicity
- Venus in Taurus labeled as detriment instead of domicile
- Saturn in Capricorn labeled as fall instead of domicile
- Mars in Aries face calculation errors
- Jupiter in Cancer missing exaltation

Tests against known good calculations using traditional astrological principles.
"""

import pytest
from app.core.ephemeris.tools.dignities import EssentialDignitiesCalculator
from app.core.ephemeris.const import SwePlanets
from app.core.ephemeris.data.dignity_loader import get_dignity_loader


class TestEssentialDignitiesFixes:
    """Test essential dignities calculation fixes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = EssentialDignitiesCalculator(use_modern_rulers=True)
        self.data_loader = get_dignity_loader()

    def test_sun_in_gemini_11_degrees(self):
        """Test Sun in Gemini 11°26'52" - should NOT have exaltation or triplicity."""
        # Sun at 11°26'52" Gemini (longitude = 71.448°)
        longitude = 71.448  # 11°26'52" into Gemini
        result = self.calculator.calculate_dignities(
            SwePlanets.SUN, longitude, is_day_chart=True
        )
        
        # Sun should NOT have exaltation (exalted in Aries, not Gemini)
        assert result.exaltation_score == 0, f"Sun should not be exalted in Gemini, got {result.exaltation_score}"
        
        # Sun should NOT have triplicity in Air signs during day chart
        # (Sun is day ruler of Fire, not Air)
        assert result.triplicity_score == 0, f"Sun should not have triplicity in Gemini (Air), got {result.triplicity_score}"
        
        # Sun should have term dignity (Jupiter rules 7-14° Gemini)
        assert result.term_score == 2, f"Sun should have term dignity in Gemini 11°, got {result.term_score}"
        
        # Verify dignities held list
        assert "exaltation" not in result.dignities_held
        assert "triplicity" not in result.dignities_held
        assert "term" in result.dignities_held

    def test_venus_in_taurus_26_degrees(self):
        """Test Venus in Taurus 26°50'52" - should be domicile, NOT detriment."""
        # Venus at 26°50'52" Taurus (longitude = 56.848°)
        longitude = 56.848  # 26°50'52" into Taurus
        result = self.calculator.calculate_dignities(
            SwePlanets.VENUS, longitude, is_day_chart=True
        )
        
        # Venus should have domicile (rules Taurus)
        assert result.rulership_score == 5, f"Venus should have domicile in Taurus, got {result.rulership_score}"
        
        # Venus should NOT have detriment
        assert result.rulership_score > 0, "Venus should not be in detriment in Taurus"
        
        # Venus should have face dignity (Mercury rules 20-30° Taurus)
        assert result.face_score == 1, f"Venus should have face dignity in Taurus 26°, got {result.face_score}"
        
        # Venus should have term dignity (Saturn rules 22-27° Taurus)
        assert result.term_score == 2, f"Venus should have term dignity in Taurus 26°, got {result.term_score}"
        
        # Verify dignities held
        assert "rulership" in result.dignities_held
        assert "detriment" not in result.debilities_held
        assert "face" in result.dignities_held
        assert "term" in result.dignities_held
        
        # Total score should be significant (5 + 2 + 1 = 8)
        assert result.total_score == 8, f"Venus total score should be 8, got {result.total_score}"

    def test_saturn_in_capricorn_14_degrees(self):
        """Test Saturn in Capricorn 14°19'17" - should be domicile, NOT fall."""
        # Saturn at 14°19'17" Capricorn (longitude = 284.321°)
        longitude = 284.321  # 14°19'17" into Capricorn
        result = self.calculator.calculate_dignities(
            SwePlanets.SATURN, longitude, is_day_chart=True
        )
        
        # Saturn should have domicile (rules Capricorn)
        assert result.rulership_score == 5, f"Saturn should have domicile in Capricorn, got {result.rulership_score}"
        
        # Saturn should NOT be in fall
        assert result.exaltation_score >= 0, "Saturn should not be in fall in Capricorn"
        
        # Saturn should have term dignity (Venus rules 14-22° Capricorn)
        assert result.term_score == 2, f"Saturn should have term dignity in Capricorn 14°, got {result.term_score}"
        
        # Verify dignities held
        assert "rulership" in result.dignities_held
        assert "fall" not in result.debilities_held
        assert "term" in result.dignities_held
        
        # Total score should be positive (5 + 2 = 7)
        assert result.total_score == 7, f"Saturn total score should be 7, got {result.total_score}"

    def test_mars_in_aries_11_degrees(self):
        """Test Mars in Aries 11°26'52" - face should be Sun's, not Mars'."""
        # Mars at 11°26'52" Aries (longitude = 11.448°)
        longitude = 11.448  # 11°26'52" into Aries
        result = self.calculator.calculate_dignities(
            SwePlanets.MARS, longitude, is_day_chart=True
        )
        
        # Mars should have domicile (rules Aries)
        assert result.rulership_score == 5, f"Mars should have domicile in Aries, got {result.rulership_score}"
        
        # Mars should have term dignity (Venus rules 6-14° Aries)
        assert result.term_score == 2, f"Mars should have term dignity in Aries 11°, got {result.term_score}"
        
        # Mars should NOT have face dignity (Sun rules 10-20° Aries, not Mars)
        assert result.face_score == 0, f"Mars should not have face dignity at Aries 11° (Sun's face), got {result.face_score}"
        
        # Total score should be 7 (5 + 2), not including face
        assert result.total_score == 7, f"Mars total score should be 7, got {result.total_score}"
        
        # Verify dignities held
        assert "rulership" in result.dignities_held
        assert "term" in result.dignities_held
        assert "face" not in result.dignities_held

    def test_jupiter_in_cancer_14_degrees(self):
        """Test Jupiter in Cancer 14°19'17" - should have exaltation."""
        # Jupiter at 14°19'17" Cancer (longitude = 104.321°)
        longitude = 104.321  # 14°19'17" into Cancer
        result = self.calculator.calculate_dignities(
            SwePlanets.JUPITER, longitude, is_day_chart=True
        )
        
        # Jupiter should have exaltation (exalted at 15° Cancer)
        assert result.exaltation_score == 4, f"Jupiter should be exalted in Cancer, got {result.exaltation_score}"
        
        # Jupiter should have term dignity (rules 19-28° Cancer - needs verification)
        # Note: This may need adjustment based on exact Egyptian terms
        
        # Verify exaltation is recognized
        assert "exaltation" in result.dignities_held
        
        # Total score should include exaltation
        assert result.total_score >= 4, f"Jupiter should have at least exaltation score, got {result.total_score}"

    def test_reference_data_loading(self):
        """Test that reference data loads correctly and matches expectations."""
        # Test dignity database loading
        db = self.data_loader.load_essential_dignities_database()
        
        # Verify key planets are present
        assert "Sun" in db["planets"], "Sun missing from planets database"
        assert "Venus" in db["planets"], "Venus missing from planets database"
        assert "Saturn" in db["planets"], "Saturn missing from planets database"
        
        # Test specific dignities
        sun_data = db["planets"]["Sun"]
        assert "Leo" in sun_data["domiciles"], "Sun should rule Leo"
        assert sun_data["exaltation"]["sign"] == "Aries", "Sun should be exalted in Aries"
        
        venus_data = db["planets"]["Venus"]
        assert "Taurus" in venus_data["domiciles"], "Venus should rule Taurus"
        assert "Scorpio" not in venus_data["domiciles"], "Venus should not rule Scorpio"

    def test_triplicity_calculations_day_night(self):
        """Test triplicity calculations work correctly for day/night charts."""
        # Test Sun as day ruler of Fire signs
        aries_longitude = 15.0  # 15° Aries
        
        # Day chart - Sun should have triplicity
        day_result = self.calculator.calculate_dignities(
            SwePlanets.SUN, aries_longitude, is_day_chart=True
        )
        assert day_result.triplicity_score == 3, "Sun should have triplicity in Fire sign during day"
        
        # Night chart - Jupiter should have triplicity (not Sun)
        jupiter_day_result = self.calculator.calculate_dignities(
            SwePlanets.JUPITER, aries_longitude, is_day_chart=False
        )
        assert jupiter_day_result.triplicity_score == 3, "Jupiter should have triplicity in Fire sign at night"

    def test_performance_benchmarks(self):
        """Test that dignity calculations meet performance targets (<2ms)."""
        import time
        
        # Test individual calculation performance
        start_time = time.time()
        for _ in range(100):  # 100 calculations
            self.calculator.calculate_dignities(
                SwePlanets.SUN, 45.0, is_day_chart=True
            )
        end_time = time.time()
        
        avg_time_ms = ((end_time - start_time) / 100) * 1000
        assert avg_time_ms < 2.0, f"Average calculation time {avg_time_ms:.2f}ms exceeds 2ms target"

    def test_batch_processing_improvement(self):
        """Test that batch processing provides performance improvement."""
        import time
        from unittest.mock import Mock
        
        # Create mock planet data
        mock_planets = {}
        for i, planet_id in enumerate([0, 1, 2, 3, 4, 5, 6]):
            mock_data = Mock()
            mock_data.longitude = 30.0 * i  # Spread across zodiac
            mock_planets[planet_id] = mock_data
        
        # Test batch processing
        start_time = time.time()
        batch_result = self.calculator.calculate_batch_dignities(
            mock_planets, is_day_chart=True
        )
        batch_time = time.time() - start_time
        
        # Test individual processing
        start_time = time.time()
        individual_results = {}
        for planet_id, mock_data in mock_planets.items():
            individual_results[planet_id] = self.calculator.calculate_dignities(
                planet_id, mock_data.longitude, is_day_chart=True
            )
        individual_time = time.time() - start_time
        
        # Batch should be at least as fast as individual
        assert batch_time <= individual_time, f"Batch processing should be faster: {batch_time:.4f}s vs {individual_time:.4f}s"

@pytest.mark.benchmark(group="dignities")
def test_dignity_calculation_benchmark(benchmark):
    """Benchmark dignity calculation performance."""
    calculator = EssentialDignitiesCalculator()
    
    result = benchmark(
        calculator.calculate_dignities,
        SwePlanets.SUN, 45.0, True
    )
    
    # Verify result is valid
    assert result is not None
    assert hasattr(result, 'total_score')