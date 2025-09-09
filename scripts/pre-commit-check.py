#!/usr/bin/env python3
"""Run before allowing commits to prevent duplicate files and maintain organization."""

import os
import sys
from pathlib import Path

def check_for_duplicates():
    """Prevent duplicate file creation."""
    files = {}
    duplicates_found = []
    
    for path in Path('backend').rglob('*.py'):
        basename = path.stem
        if basename in files:
            duplicates_found.append((path, files[basename]))
        files[basename] = path
    
    if duplicates_found:
        print("❌ Duplicate files detected:")
        for new_path, existing_path in duplicates_found:
            print(f"   {new_path} conflicts with {existing_path}")
        return False
    
    print("✅ No duplicate files found")
    return True

def check_file_locations():
    """Ensure files are in correct directories."""
    issues = []
    
    # Check for test files in root
    root_tests = list(Path('.').glob('test_*.py'))
    if root_tests:
        issues.append(f"❌ Test files in root: {[str(f) for f in root_tests]}")
        issues.append("   Move them to backend/tests/")
    
    # Check for large data files in root
    root_data = list(Path('.').glob('*.json'))
    large_root_data = [f for f in root_data if f.stat().st_size > 1000]
    if large_root_data:
        issues.append(f"❌ Large data files in root: {[str(f) for f in large_root_data]}")
        issues.append("   Move them to backend/data/")
    
    # Check for Python scripts in root (except main entry points)
    allowed_root_scripts = {'main.py', 'manage.py', 'run.py'}
    root_scripts = [f for f in Path('.').glob('*.py') 
                   if f.name not in allowed_root_scripts and 
                   not f.name.startswith('setup')]
    if root_scripts:
        issues.append(f"❌ Utility scripts in root: {[str(f) for f in root_scripts]}")
        issues.append("   Move them to scripts/")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    
    print("✅ All files in correct locations")
    return True

def check_for_temp_files():
    """Find temporary or working files that shouldn't be committed."""
    temp_patterns = ['*temp*', '*working*', '*backup*', '*old*', '*new*', '*test*']
    temp_files = []
    
    for pattern in temp_patterns:
        temp_files.extend(Path('.').glob(pattern))
    
    # Filter out legitimate files
    legitimate = {'working_fixed_stars.json', 'test_fixed_stars.py'}  # These are legitimate
    temp_files = [f for f in temp_files if f.name not in legitimate and 
                 not f.is_dir() and 
                 not str(f).startswith(('.git', 'backend/tests', 'backend/venv'))]
    
    if temp_files:
        print(f"❌ Temporary files detected: {[str(f) for f in temp_files]}")
        print("   Remove or rename these files")
        return False
    
    print("✅ No temporary files found")
    return True

def check_comprehensive_file():
    """Check if comprehensive ephemeris file is too large."""
    comprehensive_files = list(Path('.').glob('COMPREHENSIVE_EPHEMERIS_STRUCTURE*.json'))
    
    for file in comprehensive_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        if size_mb > 50:  # 50MB threshold
            print(f"⚠️  Large comprehensive file: {file} ({size_mb:.1f}MB)")
            print("   Consider moving to backend/data/ or compressing")
            return False
    
    return True

def main():
    """Run all checks."""
    print("🔍 Running pre-commit validations...")
    
    checks = [
        ("Duplicate files", check_for_duplicates()),
        ("File locations", check_file_locations()),
        ("Temporary files", check_for_temp_files()),
        ("Large files", check_comprehensive_file()),
    ]
    
    all_passed = all(passed for _, passed in checks)
    
    if not all_passed:
        print("\n❌ Pre-commit checks failed!")
        print("Fix the issues above before committing.")
        sys.exit(1)
    else:
        print("\n✅ All pre-commit checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
