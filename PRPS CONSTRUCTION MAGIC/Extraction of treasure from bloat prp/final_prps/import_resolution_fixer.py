#!/usr/bin/env python3
"""
Import Resolution Fixer - Automated import resolution for extracted systems
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import shutil

class ImportResolutionFixer:
    """Fixes import statements and creates proper module structure during extraction"""
    
    def __init__(self):
        # Comprehensive import mapping patterns
        self.import_mapping = {
            # Backend module mappings
            r'from backend\.app\.core\.ephemeris\.tools\.([a-zA-Z_]+)': r'from extracted.systems.\1',
            r'from backend\.app\.core\.ephemeris\.tools': 'from extracted.systems',
            r'from backend\.app\.core\.ephemeris\.models': 'from extracted.systems.models',
            r'from backend\.app\.core\.ephemeris\.const': 'from extracted.systems.utils.const',
            r'from backend\.app\.core\.ephemeris': 'from extracted.systems',
            r'from backend\.app\.core\.acg': 'from extracted.systems.acg_engine',
            r'from backend\.app\.services': 'from extracted.services',
            r'from backend\.app\.api': 'from extracted.api',
            
            # App module mappings
            r'from app\.core\.ephemeris\.tools\.([a-zA-Z_]+)': r'from extracted.systems.\1',
            r'from app\.core\.ephemeris\.tools': 'from extracted.systems',
            r'from app\.core\.ephemeris\.models': 'from extracted.systems.models',
            r'from app\.core\.ephemeris': 'from extracted.systems',
            r'from app\.core\.acg': 'from extracted.systems.acg_engine',
            r'from app\.services': 'from extracted.services',
            r'from app\.api': 'from extracted.api',
            
            # Relative imports
            r'from \.\.const': 'from extracted.systems.utils.const',
            r'from \.\.models': 'from extracted.systems.models',
            r'from \.ephemeris': 'from extracted.systems.ephemeris_utils',
            r'from \.\.ephemeris': 'from extracted.systems.ephemeris_utils',
            
            # Import statements
            r'import backend\.app\.core\.ephemeris': 'import extracted.systems',
            r'import backend\.app\.core\.acg': 'import extracted.systems.acg_engine',
            r'import app\.core\.ephemeris': 'import extracted.systems',
        }
        
        # Common code fixes during extraction
        self.common_fixes = [
            # Pydantic v2 compatibility
            (r'\.dict\(\)', '.model_dump()'),
            (r'\.json\(\)', '.model_dump_json()'),
            (r'from pydantic import BaseSettings', 'from pydantic_settings import BaseSettings'),
            
            # Swiss Ephemeris path setup fixes
            (r'_setup_swisseph_path\(\)', '_setup_swiss_ephemeris_path()'),
            
            # Logger setup fixes
            (r'logger = logging\.getLogger\(__name__\)', 
             'logger = logging.getLogger(__name__)\\nif not logger.handlers: logging.basicConfig(level=logging.INFO)'),
        ]
        
        # Files that need special handling
        self.special_files = {
            'fixed_stars.py': self._fix_fixed_stars_imports,
            'arabic_parts.py': self._fix_arabic_parts_imports, 
            'acg_core.py': self._fix_acg_core_imports,
        }
    
    def _fix_fixed_stars_imports(self, content: str) -> str:
        """Special fixes for fixed_stars.py"""
        fixes = [
            # Swiss Ephemeris wrapper
            (r'import swisseph as swe', 
             'import swisseph as swe\nfrom .utils.swiss_ephemeris import ensure_swiss_ephemeris_setup'),
            
            # Star registry imports
            (r'from \.\.const import normalize_longitude',
             'from extracted.systems.utils.const import normalize_longitude'),
             
            (r'from \.ephemeris import PlanetPosition',
             'from extracted.systems.models.planet_position import PlanetPosition'),
        ]
        
        for old, new in fixes:
            content = re.sub(old, new, content)
            
        return content
    
    def _fix_arabic_parts_imports(self, content: str) -> str:
        """Special fixes for arabic_parts.py"""
        fixes = [
            # Formula imports
            (r'from \.arabic_parts_formulas import',
             'from .arabic_parts_formulas import'),
            
            # Model imports  
            (r'from \.arabic_parts_models import',
             'from .arabic_parts_models import'),
             
            # Sect calculator
            (r'from \.sect_calculator import',
             'from .sect_calculator import'),
        ]
        
        for old, new in fixes:
            content = re.sub(old, new, content)
            
        return content
    
    def _fix_acg_core_imports(self, content: str) -> str:
        """Special fixes for acg_core.py"""
        fixes = [
            # ACG relative import normalizations
            (r'from \.acg_utils import', 'from .acg_utils import'),
            (r'from \.acg_types import', 'from .acg_types import'),
            (r'from \.acg_cache import', 'from .acg_cache import'),
            # Ensure legacy BaseSettings import is updated to pydantic_settings
            (r'from pydantic import BaseSettings', 'from pydantic_settings import BaseSettings'),
            # Logger setup fixes (ensure basicConfig only added when no handlers)
            (r'logger = logging\.getLogger\(__name__\)', 'logger = logging.getLogger(__name__)\\nif not logger.handlers: logging.basicConfig(level=logging.INFO)'),
        ]
        
        for old, new in fixes:
            content = re.sub(old, new, content)
            
        return content
    
    def fix_file_imports(self, file_path: str) -> List[str]:
        """Fix imports in a single file and return list of changes made"""
        changes = []
        
        # Skip unsafe paths
        if self._should_skip_path(file_path):
            return []

        if not os.path.exists(file_path):
            return [f"File not found: {file_path}"]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Apply general import mappings
        for old_pattern, new_replacement in self.import_mapping.items():
            old_content = content
            content = re.sub(old_pattern, new_replacement, content)
            if content != old_content:
                # Count number of replacements
                matches = len(re.findall(old_pattern, old_content))
                changes.append(f"Import mapping ({matches}x): {old_pattern} -> {new_replacement}")
                
        # Apply common fixes
        for old_pattern, new_replacement in self.common_fixes:
            old_content = content
            content = re.sub(old_pattern, new_replacement, content)
            if content != old_content:
                matches = len(re.findall(old_pattern, old_content))
                changes.append(f"Code fix ({matches}x): {old_pattern}")
                
        # Apply special file fixes
        filename = os.path.basename(file_path)
        if filename in self.special_files:
            old_content = content
            content = self.special_files[filename](content)
            if content != old_content:
                changes.append(f"Special fixes applied for {filename}")
        
        # Write back if changes were made
        if content != original_content:
            # Backup original file
            backup_path = file_path + '.backup'
            shutil.copy2(file_path, backup_path)
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            changes.append(f"File updated (backup: {backup_path})")
                
        return changes
    
    def fix_directory_imports(self, directory_path: str) -> Dict[str, List[str]]:
        """Fix imports in all Python files in a directory"""
        results = {}
        
        if not os.path.exists(directory_path):
            return {"ERROR": [f"Directory not found: {directory_path}"]}
        
        for root, dirs, files in os.walk(directory_path):
            # Prune directories we must not touch
            self._prune_unsafe_dirs(dirs)
            # Skip entire tree if root is unsafe
            if self._should_skip_path(root):
                continue
            for file in files:
                if file.endswith('.py') and not file.endswith('.backup'):
                    file_path = os.path.join(root, file)
                    changes = self.fix_file_imports(file_path)
                    if changes:
                        rel_path = os.path.relpath(file_path, directory_path)
                        results[rel_path] = changes
                        
        return results

    # ----------------- internal helpers -----------------
    def _should_skip_path(self, path: str) -> bool:
        """Return True if the path points into a virtual env, site-packages, caches, or vendor dirs"""
        lowered = path.replace('\\', '/').lower()
        skip_substrings = [
            '/.venv/', '/venv/', '/env/', '/.env/',
            '/site-packages/', '/dist-packages/',
            '/node_modules/', '/.git/', '/__pycache__/'
        ]
        return any(s in lowered for s in skip_substrings)

    def _prune_unsafe_dirs(self, dirs: List[str]) -> None:
        """Remove unsafe directory names from os.walk traversal in-place"""
        unsafe = {
            '.venv', 'venv', 'env', '.env',
            'site-packages', 'dist-packages',
            'node_modules', '.git', '__pycache__'
        }
        # mutate in place
        dirs[:] = [d for d in dirs if d not in unsafe]
    
    def create_module_structure(self, base_path: str = "."):
        """Create complete module structure for extracted systems"""
        
        # Directory structure to create
        directories = [
            "extracted",
            "extracted/systems", 
            "extracted/systems/fixed_stars",
            "extracted/systems/arabic_parts",
            "extracted/systems/aspects", 
            "extracted/systems/acg_engine",
            "extracted/systems/models",
            "extracted/systems/utils",
            "extracted/services",
            "extracted/api",
            "tests/extraction",
            "tests/integration", 
            "tests/perf"
        ]
        
        # __init__.py files with specific content
        init_files = {
            "extracted/__init__.py": '''"""Extracted astrology calculation systems"""
__version__ = "1.0.0"
''',
            "extracted/systems/__init__.py": '''"""Core astrology calculation systems"""
from .fixed_stars import FixedStarCalculator
from .arabic_parts import ArabicPartsCalculator
from .aspects import AspectCalculator
from .acg_engine import ACGCalculationEngine

__all__ = [
    "FixedStarCalculator",
    "ArabicPartsCalculator", 
    "AspectCalculator",
    "ACGCalculationEngine"
]
''',
            "extracted/systems/utils/__init__.py": '''"""Utility modules for astrology calculations"""
from .swiss_ephemeris import ensure_swiss_ephemeris_setup, safe_fixstar, safe_calc_ut

__all__ = ["ensure_swiss_ephemeris_setup", "safe_fixstar", "safe_calc_ut"]
''',
            "extracted/systems/models/__init__.py": '''"""Data models for astrology calculations"""
# Import common models here when available
''',
        }
        
        # Create directories
        created_dirs = []
        for directory in directories:
            dir_path = os.path.join(base_path, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                created_dirs.append(directory)
                
        # Create __init__.py files
        created_inits = []
        for init_path, content in init_files.items():
            full_path = os.path.join(base_path, init_path)
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_inits.append(init_path)
                
        # Create remaining __init__.py files (empty)
        remaining_inits = []
        for directory in directories:
            init_path = os.path.join(base_path, directory, "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, 'w', encoding='utf-8') as f:
                    f.write('"""Auto-generated __init__.py"""\n')
                remaining_inits.append(os.path.join(directory, "__init__.py"))
                
        return {
            "directories_created": created_dirs,
            "init_files_created": created_inits + remaining_inits
        }
    
    def create_swiss_ephemeris_wrapper(self, base_path: str = "."):
        """Create Swiss Ephemeris wrapper module"""
        wrapper_content = '''"""
Swiss Ephemeris wrapper for extracted systems - Auto-setup and safe calls
"""

import os
import sys
from pathlib import Path
import swisseph as swe

# Global Swiss Ephemeris state
_SWISS_EPH_INITIALIZED = False
_SWISS_EPH_PATH = None

def setup_swiss_ephemeris_for_extraction(base_path: str = None) -> str:
    """Setup Swiss Ephemeris with multiple fallback strategies"""
    global _SWISS_EPH_PATH
    
    if base_path is None:
        # Auto-detect project root
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "Swiss Eph Library Files").exists():
                base_path = str(parent)
                break
        else:
            base_path = str(Path.cwd())
    
    # Search paths in order of preference
    search_paths = [
        os.path.join(base_path, "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "..", "Swiss Eph Library Files"),
        os.path.join(base_path, "..", "..", "..", "Swiss Eph Library Files"),
        os.environ.get('SE_EPHE_PATH', ''),
        "/usr/share/swisseph",
        "C:/swisseph"
    ]
    
    for search_path in search_paths:
        if not search_path or not os.path.exists(search_path):
            continue
            
        # Verify critical files
        sefstars_path = os.path.join(search_path, "sefstars.txt")
        if os.path.exists(sefstars_path):
            try:
                swe.set_ephe_path(search_path)
                os.environ['SE_EPHE_PATH'] = search_path
                
                # Quick validation test
                test_result = swe.fixstar("Regulus", 2460000.5)
                if test_result and len(test_result) >= 2:
                    _SWISS_EPH_PATH = search_path
                    return search_path
                    
            except Exception:
                continue
    
    # If all paths fail
    raise RuntimeError(f"""
Swiss Ephemeris setup failed! 

Searched paths:
{chr(10).join(f'  - {path}' for path in search_paths if path)}

Required: 'Swiss Eph Library Files' directory containing:
  - sefstars.txt (fixed star catalog)
  - seas_18.se1 (asteroid ephemeris)
  - sepl_18.se1 (planet ephemeris)
  - semo_18.se1 (moon ephemeris)

Solutions:
1. Ensure Swiss Ephemeris files are in project root
2. Set SE_EPHE_PATH environment variable
3. Copy files to one of the search locations
""")

def ensure_swiss_ephemeris_setup():
    """Ensure Swiss Ephemeris is properly configured (call this before any calculations)"""
    global _SWISS_EPH_INITIALIZED, _SWISS_EPH_PATH
    
    if not _SWISS_EPH_INITIALIZED:
        _SWISS_EPH_PATH = setup_swiss_ephemeris_for_extraction()
        _SWISS_EPH_INITIALIZED = True
        
    return _SWISS_EPH_PATH

def safe_fixstar(star_name: str, julian_day: float):
    """Safe fixed star calculation with automatic Swiss Ephemeris setup"""
    ensure_swiss_ephemeris_setup()
    return swe.fixstar(star_name, julian_day)

def safe_calc_ut(julian_day: float, body_id: int):
    """Safe planetary calculation with automatic Swiss Ephemeris setup"""
    ensure_swiss_ephemeris_setup()
    return swe.calc_ut(julian_day, body_id)

def safe_houses(julian_day: float, latitude: float, longitude: float, house_system: bytes = b'P'):
    """Safe house calculation with automatic Swiss Ephemeris setup
    
    Returns: (cusps, ascmc) where:
    - cusps[0] is unused, cusps[1-12] are house cusps 1-12
    - ascmc[0-3] are ASC, MC, ARMC, Vertex
    """
    ensure_swiss_ephemeris_setup()
    return swe.houses(julian_day, latitude, longitude, house_system)

# Auto-setup on module import (with error handling)
try:
    ensure_swiss_ephemeris_setup()
    print(f"✅ Swiss Ephemeris auto-configured: {_SWISS_EPH_PATH}")
except Exception as e:
    print(f"⚠️  Swiss Ephemeris auto-setup failed: {e}")
    print("   Manual setup may be required before calculations")
    _SWISS_EPH_INITIALIZED = False
'''
        
        # Create utils directory if needed
        utils_dir = os.path.join(base_path, "extracted", "systems", "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        # Write wrapper
        wrapper_path = os.path.join(utils_dir, "swiss_ephemeris.py")
        with open(wrapper_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
            
        print(f"✅ Swiss Ephemeris wrapper created: {wrapper_path}")
        return wrapper_path

def main():
    """Command line interface for import resolution fixer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix imports for extracted astrology systems')
    parser.add_argument('path', nargs='?', default='.', help='Directory or file to fix (default: current)')
    parser.add_argument('--setup', action='store_true', help='Create module structure only')
    parser.add_argument('--wrapper', action='store_true', help='Create Swiss Ephemeris wrapper')
    
    args = parser.parse_args()
    
    fixer = ImportResolutionFixer()
    
    if args.setup:
        print("📁 Creating module structure...")
        result = fixer.create_module_structure()
        print(f"✅ Created {len(result['directories_created'])} directories")
        print(f"✅ Created {len(result['init_files_created'])} __init__.py files")
        
    if args.wrapper:
        print("🔧 Creating Swiss Ephemeris wrapper...")
        wrapper_path = fixer.create_swiss_ephemeris_wrapper()
        print(f"✅ Wrapper created: {wrapper_path}")
        
    if not args.setup and not args.wrapper:
        # Fix imports in specified path
        if os.path.isfile(args.path):
            print(f"🔧 Fixing imports in file: {args.path}")
            changes = fixer.fix_file_imports(args.path)
            if changes:
                print("Changes made:")
                for change in changes:
                    print(f"  - {change}")
            else:
                print("No changes needed")
        else:
            print(f"🔧 Fixing imports in directory: {args.path}")
            results = fixer.fix_directory_imports(args.path)
            
            if results:
                print(f"Fixed imports in {len(results)} files:")
                for file, changes in results.items():
                    print(f"  📄 {file}:")
                    for change in changes:
                        print(f"    - {change}")
            else:
                print("No Python files found or no changes needed")

if __name__ == "__main__":
    main()
