# SWISS EPHEMERIS INTEGRATION VALIDATOR

## Purpose
Comprehensive Swiss Ephemeris setup validation and automated import resolution for extracted systems.

## Swiss Ephemeris Setup Validation

### 1. Data File Verification
```python
# swiss_ephemeris_validator.py
"""Swiss Ephemeris integration validation for extracted systems"""

import os
import sys
from pathlib import Path
import swisseph as swe

class SwissEphemerisValidator:
    """Validates Swiss Ephemeris setup for extracted systems"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = str(Path(__file__).parent.parent.parent)
        self.project_root = project_root
        self.swiss_eph_path = None
        
    def validate_data_files(self) -> bool:
        """Validate all required Swiss Ephemeris data files exist"""
        required_files = [
            "sefstars.txt",   # Fixed star catalog (CRITICAL for fixed stars)
            "seas_18.se1",    # Asteroid ephemeris  
            "semo_18.se1",    # Moon ephemeris
            "sepl_18.se1"     # Planet ephemeris
        ]
        
        swiss_path = os.path.join(self.project_root, "Swiss Eph Library Files")
        
        if not os.path.exists(swiss_path):
            print(f"❌ Swiss Ephemeris directory not found: {swiss_path}")
            return False
            
        missing_files = []
        for file in required_files:
            file_path = os.path.join(swiss_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
            else:
                file_size = os.path.getsize(file_path)
                print(f"✅ {file}: {file_size:,} bytes")
        
        if missing_files:
            print(f"❌ Missing Swiss Ephemeris files: {missing_files}")
            return False
            
        self.swiss_eph_path = swiss_path
        return True
        
    def setup_swiss_ephemeris(self) -> bool:
        """Setup Swiss Ephemeris path for calculations"""
        if not self.swiss_eph_path:
            if not self.validate_data_files():
                return False
                
        try:
            swe.set_ephe_path(self.swiss_eph_path)
            os.environ['SE_EPHE_PATH'] = self.swiss_eph_path
            print(f"✅ Swiss Ephemeris path set: {self.swiss_eph_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to set Swiss Ephemeris path: {e}")
            return False
            
    def test_fixed_star_calculation(self) -> bool:
        """Test fixed star calculation functionality"""
        if not self.setup_swiss_ephemeris():
            return False
            
        test_stars = ["Regulus", "Aldebaran", "Antares", "Fomalhaut"]
        test_jd = 2460000.5  # Reference Julian Day
        
        working_stars = []
        for star_name in test_stars:
            try:
                result = swe.fixstar(star_name, test_jd)
                if len(result) >= 2 and isinstance(result[0], (list, tuple)):
                    longitude = result[0][0]
                    if 0 <= longitude <= 360:
                        working_stars.append(star_name)
                        print(f"✅ {star_name}: {longitude:.2f}°")
                    else:
                        print(f"❌ {star_name}: Invalid longitude {longitude}")
                else:
                    print(f"❌ {star_name}: Invalid result format")
            except Exception as e:
                print(f"❌ {star_name}: Calculation failed - {e}")
                
        success_rate = len(working_stars) / len(test_stars)
        print(f"Fixed star calculation success rate: {success_rate:.1%}")
        return success_rate >= 0.75  # At least 75% success rate
        
    def test_planetary_calculation(self) -> bool:
        """Test planetary position calculation"""
        if not self.setup_swiss_ephemeris():
            return False
            
        test_bodies = [
            (0, "Sun"), (1, "Moon"), (2, "Mercury"), (3, "Venus"), 
            (4, "Mars"), (5, "Jupiter"), (6, "Saturn")
        ]
        test_jd = 2460000.5
        
        working_bodies = []
        for body_id, body_name in test_bodies:
            try:
                result = swe.calc_ut(test_jd, body_id)
                if len(result) >= 2 and isinstance(result[0], (list, tuple)):
                    longitude = result[0][0]
                    if 0 <= longitude <= 360:
                        working_bodies.append(body_name)
                        print(f"✅ {body_name}: {longitude:.2f}°")
                    else:
                        print(f"❌ {body_name}: Invalid longitude {longitude}")
                else:
                    print(f"❌ {body_name}: Invalid result format")
            except Exception as e:
                print(f"❌ {body_name}: Calculation failed - {e}")
                
        success_rate = len(working_bodies) / len(test_bodies)
        print(f"Planetary calculation success rate: {success_rate:.1%}")
        return success_rate >= 0.85  # At least 85% success rate
        
    def validate_all(self) -> bool:
        """Run complete Swiss Ephemeris validation"""
        print("🔍 Starting Swiss Ephemeris validation...")
        
        results = {
            "data_files": self.validate_data_files(),
            "setup": self.setup_swiss_ephemeris(),
            "fixed_stars": self.test_fixed_star_calculation(),
            "planets": self.test_planetary_calculation()
        }
        
        all_passed = all(results.values())
        
        print(f"\n📊 Validation Results:")
        for test, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {test}: {status}")
            
        if all_passed:
            print(f"\n🎉 Swiss Ephemeris fully validated and ready!")
        else:
            print(f"\n⚠️  Swiss Ephemeris validation failed. Check errors above.")
            
        return all_passed

if __name__ == "__main__":
    validator = SwissEphemerisValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)
```

### 2. Usage in Extraction
```python
# Add to each PRP extraction validation
def validate_swiss_ephemeris_before_extraction():
    from swiss_ephemeris_validator import SwissEphemerisValidator
    validator = SwissEphemerisValidator()
    if not validator.validate_all():
        raise RuntimeError("Swiss Ephemeris validation failed - extraction cannot proceed")
    return validator.swiss_eph_path
```

## Import Resolution Automation

### 1. Automated Import Fixer
```python
# import_resolution_fixer.py
"""Automated import resolution for extracted systems"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ImportResolutionFixer:
    """Fixes import statements during extraction process"""
    
    def __init__(self):
        self.import_mapping = {
            # Backend to extracted mappings
            r'from backend\.app\.core\.ephemeris\.tools': 'from extracted.systems',
            r'from backend\.app\.core\.ephemeris\.models': 'from extracted.systems.models',
            r'from backend\.app\.core\.ephemeris\.const': 'from extracted.systems.utils',
            r'from backend\.app\.core\.acg': 'from extracted.systems.acg_engine',
            r'from backend\.app\.services': 'from extracted.services',
            r'from app\.core\.ephemeris': 'from extracted.systems',
            r'from app\.services': 'from extracted.services',
            r'import backend\.app\.core': 'import extracted.systems',
            
            # Specific module mappings
            r'\.\.const': 'extracted.systems.utils.const',
            r'\.ephemeris import': '.ephemeris_utils import',
        }
        
        self.common_fixes = [
            # Pydantic v2 compatibility
            (r'\.dict\(\)', '.model_dump()'),
            (r'from pydantic import BaseModel, Field', 'from pydantic import BaseModel, Field'),
            
            # Swiss Ephemeris path setup
            (r'swe\.set_ephe_path\(', 'self._setup_swiss_ephemeris_path(); swe.set_ephe_path('),
        ]
    
    def fix_file_imports(self, file_path: str) -> List[str]:
        """Fix imports in a single file and return list of changes made"""
        changes = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Apply import mappings
        for old_pattern, new_replacement in self.import_mapping.items():
            old_content = content
            content = re.sub(old_pattern, new_replacement, content)
            if content != old_content:
                changes.append(f"Import mapping: {old_pattern} -> {new_replacement}")
                
        # Apply common fixes
        for old_pattern, new_replacement in self.common_fixes:
            old_content = content
            content = re.sub(old_pattern, new_replacement, content)
            if content != old_content:
                changes.append(f"Code fix: {old_pattern} -> {new_replacement}")
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return changes
    
    def fix_directory_imports(self, directory_path: str) -> Dict[str, List[str]]:
        """Fix imports in all Python files in a directory"""
        results = {}
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    changes = self.fix_file_imports(file_path)
                    if changes:
                        rel_path = os.path.relpath(file_path, directory_path)
                        results[rel_path] = changes
                        
        return results
    
    def create_init_files(self, base_path: str):
        """Create necessary __init__.py files for proper Python imports"""
        init_locations = [
            "extracted/__init__.py",
            "extracted/systems/__init__.py", 
            "extracted/systems/fixed_stars/__init__.py",
            "extracted/systems/arabic_parts/__init__.py",
            "extracted/systems/aspects/__init__.py",
            "extracted/systems/acg_engine/__init__.py",
            "extracted/systems/models/__init__.py",
            "extracted/systems/utils/__init__.py",
            "extracted/services/__init__.py"
        ]
        
        for init_path in init_locations:
            full_path = os.path.join(base_path, init_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            if not os.path.exists(full_path):
                with open(full_path, 'w') as f:
                    f.write('"""Auto-generated __init__.py for extracted systems"""\n')
                print(f"✅ Created: {init_path}")

# Usage example
def apply_import_fixes_to_extraction(extraction_path: str):
    fixer = ImportResolutionFixer()
    
    # Create necessary __init__.py files
    fixer.create_init_files(".")
    
    # Fix imports in extracted files
    results = fixer.fix_directory_imports(extraction_path)
    
    print(f"Import resolution applied to {len(results)} files:")
    for file, changes in results.items():
        print(f"  📁 {file}:")
        for change in changes:
            print(f"    - {change}")
            
    return results
```

### 3. Enhanced Swiss Ephemeris Path Setup
```python
# enhanced_swiss_ephemeris_setup.py
"""Enhanced Swiss Ephemeris path setup for extracted systems"""

import os
import sys
from pathlib import Path
import swisseph as swe

def setup_swiss_ephemeris_for_extraction(base_path: str = None) -> str:
    """
    Setup Swiss Ephemeris with multiple fallback strategies for extracted systems
    
    Returns:
        Path to Swiss Ephemeris data directory
    """
    if base_path is None:
        base_path = os.getcwd()
        
    # Multiple search strategies
    search_paths = [
        # Relative to extraction location
        os.path.join(base_path, "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "..", "Swiss Eph Library Files"),
        
        # Absolute fallback (current known location)
        "c:/Users/jacks/OneDrive/Desktop/MERIDIAN/Meridian DEV/ASTRO MERIDIAN APP V1.0/Swiss Eph Library Files",
        
        # Environment variable
        os.environ.get('SE_EPHE_PATH', ''),
        
        # Standard system locations
        "/usr/share/swisseph",
        "/opt/swisseph",
        "C:/swisseph",
    ]
    
    for search_path in search_paths:
        if not search_path:
            continue
            
        if os.path.exists(search_path):
            # Verify critical files exist
            sefstars_path = os.path.join(search_path, "sefstars.txt")
            if os.path.exists(sefstars_path):
                try:
                    swe.set_ephe_path(search_path)
                    os.environ['SE_EPHE_PATH'] = search_path
                    
                    # Test with a simple calculation
                    test_result = swe.fixstar("Regulus", 2460000.5)
                    if test_result and len(test_result) >= 2:
                        print(f"✅ Swiss Ephemeris setup successful: {search_path}")
                        return search_path
                        
                except Exception as e:
                    print(f"⚠️  Swiss Ephemeris test failed for {search_path}: {e}")
                    continue
    
    # If all fails, provide clear error with setup instructions
    error_msg = """
❌ Swiss Ephemeris setup failed!

Required: Swiss Ephemeris data files (sefstars.txt, seas_18.se1, etc.)

Setup options:
1. Ensure 'Swiss Eph Library Files' directory is in project root
2. Set SE_EPHE_PATH environment variable 
3. Copy Swiss Ephemeris files to one of the search locations

Searched paths:
""" + "\n".join(f"  - {path}" for path in search_paths if path)
    
    raise RuntimeError(error_msg)

def create_swiss_ephemeris_wrapper():
    """Create a wrapper module for consistent Swiss Ephemeris access"""
    wrapper_content = '''
"""Swiss Ephemeris wrapper for extracted systems"""

import os
import swisseph as swe
from .enhanced_swiss_ephemeris_setup import setup_swiss_ephemeris_for_extraction

# Global Swiss Ephemeris setup
_SWISS_EPH_INITIALIZED = False
_SWISS_EPH_PATH = None

def ensure_swiss_ephemeris_setup():
    """Ensure Swiss Ephemeris is properly configured"""
    global _SWISS_EPH_INITIALIZED, _SWISS_EPH_PATH
    
    if not _SWISS_EPH_INITIALIZED:
        _SWISS_EPH_PATH = setup_swiss_ephemeris_for_extraction()
        _SWISS_EPH_INITIALIZED = True
        
    return _SWISS_EPH_PATH

def safe_fixstar(star_name: str, julian_day: float):
    """Safe fixed star calculation with automatic setup"""
    ensure_swiss_ephemeris_setup()
    return swe.fixstar(star_name, julian_day)

def safe_calc_ut(julian_day: float, body_id: int):
    """Safe planetary calculation with automatic setup"""
    ensure_swiss_ephemeris_setup()
    return swe.calc_ut(julian_day, body_id)

# Auto-setup on import
try:
    ensure_swiss_ephemeris_setup()
except Exception as e:
    print(f"⚠️  Swiss Ephemeris auto-setup failed: {e}")
    print("Manual setup may be required")
'''
    
    os.makedirs("extracted/systems/utils", exist_ok=True)
    with open("extracted/systems/utils/swiss_ephemeris.py", "w") as f:
        f.write(wrapper_content)
        
    print("✅ Swiss Ephemeris wrapper created")
```

## Integration with PRPs

### Usage in Enhanced PRP Tasks
```yaml
# Enhanced task example for PRP_FIXED_STARS_EXTRACTION
pre_extraction_validation:
  action: VALIDATE
  command: python swiss_ephemeris_validator.py
  expect: "Swiss Ephemeris fully validated and ready"
  on_failure: "HALT - Swiss Ephemeris setup required"

copy_source_with_import_fixes:
  action: COPY
  from: backend/app/core/ephemeris/tools/fixed_stars.py
  to: extracted/systems/fixed_stars/fixed_stars.py
  post_process:
    - python import_resolution_fixer.py extracted/systems/fixed_stars/
    - python -c "from swiss_ephemeris_validator import SwissEphemerisValidator; SwissEphemerisValidator().validate_all()"
  validate:
    - python -c "import sys; sys.path.insert(0, '.'); from extracted.systems.fixed_stars.fixed_stars import FixedStarCalculator; calc = FixedStarCalculator(); print('✅ EXTRACTION OK')"
```

This comprehensive approach ensures robust Swiss Ephemeris integration and resolves import complexity automatically during extraction.
