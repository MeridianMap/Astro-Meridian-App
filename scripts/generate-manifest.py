#!/usr/bin/env python3
"""Create manifest of current project state for AI reference."""

import os
import json
from pathlib import Path
from datetime import datetime

def create_session_manifest():
    """Create a manifest of current state for AI reference."""
    
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "project_name": "Meridian Ephemeris API",
        "branch": get_git_branch(),
        "commit_hash": get_git_commit_hash(),
        "total_lines_of_code": 0,
        "complexity_score": 0,
        "existing_modules": {},
        "test_files": [],
        "data_files": [],
        "config_files": [],
        "api_routes": [],
        "recent_changes": get_recent_changes(),
        "architecture_quality": {},
        "architecture_rules": {
            "single_source_of_truth": True,
            "modify_not_create": True,
            "proper_locations": {
                "code": "backend/app/",
                "tests": "backend/tests/",
                "data": "backend/data/",
                "docs": "docs/",
                "scripts": "scripts/"
            }
        },
        "critical_files": {
            "main_api": "backend/app/main.py",
            "swiss_eph": "Swiss Eph Library Files/",
            "fixed_stars": "backend/data/working_fixed_stars.json",
            "documentation": "CLAUDE.md"
        }
    }
    
    # Map all Python modules in backend/app
    app_path = Path('backend/app')
    if app_path.exists():
        for path in app_path.rglob('*.py'):
            if path.name != '__init__.py':
                module_name = path.stem
                relative_path = path.relative_to(Path('.'))
                manifest["existing_modules"][module_name] = {
                    "path": str(relative_path),
                    "size": path.stat().st_size,
                    "purpose": categorize_module(path),
                    "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
                manifest["total_lines_of_code"] += count_lines_of_code(path)
    
    # Calculate architecture quality metrics
    manifest["architecture_quality"] = calculate_architecture_quality(manifest)
    
    # Calculate complexity score
    manifest["complexity_score"] = calculate_complexity_score(manifest)
    
    # Map test files
    test_path = Path('backend/tests')
    if test_path.exists():
        for path in test_path.rglob('test_*.py'):
            manifest["test_files"].append({
                "name": path.stem,
                "path": str(path.relative_to(Path('.'))),
                "size": path.stat().st_size,
                "tests_module": path.stem.replace('test_', '')
            })
    
    # Map data files
    for ext in ['.json', '.yaml', '.csv', '.xml']:
        for path in Path('.').rglob(f'*{ext}'):
            if (path.stat().st_size > 100 and  # Only significant files
                not any(skip in str(path) for skip in ['venv', '__pycache__', '.git', 'node_modules'])):
                manifest["data_files"].append({
                    "name": path.name,
                    "path": str(path.relative_to(Path('.'))),
                    "size": path.stat().st_size,
                    "type": ext[1:]  # Remove the dot
                })
    
    # Map configuration files
    config_patterns = ['*.yml', '*.yaml', '*.toml', '*.ini', '*.conf', 'docker*', 'requirements*.txt']
    for pattern in config_patterns:
        for path in Path('.').glob(pattern):
            manifest["config_files"].append({
                "name": path.name,
                "path": str(path.relative_to(Path('.'))),
                "type": "configuration"
            })
    
    # Try to identify API routes
    try:
        api_routes_path = Path('backend/app/api/routes')
        if api_routes_path.exists():
            for route_file in api_routes_path.glob('*.py'):
                if route_file.name != '__init__.py':
                    manifest["api_routes"].append({
                        "name": route_file.stem,
                        "path": str(route_file.relative_to(Path('.')))
                    })
    except:
        pass
    
    # Save manifest
    with open('.agentic-manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2, default=str)
    
    print(f"✅ Manifest created: .agentic-manifest.json")
    print(f"📁 Tracked {len(manifest['existing_modules'])} modules")
    print(f"🧪 Found {len(manifest['test_files'])} test files")
    print(f"📊 Found {len(manifest['data_files'])} data files")
    print(f"🛣️  Found {len(manifest['api_routes'])} API route files")
    print(f"📏 Total lines of code: {manifest['total_lines_of_code']}")
    print(f"🔢 Complexity score: {manifest['complexity_score']}")
    print(f"🏗️  Architecture quality:")
    print(f"   - Test coverage ratio: {manifest['architecture_quality']['test_coverage']:.2f}")
    print(f"   - Large files: {len(manifest['architecture_quality']['large_files'])}")
    print(f"   - Potential redundancies: {len(manifest['architecture_quality']['redundancy_indicators'])}")
    
    # Branch comparison advice
    if manifest['complexity_score'] < 50:
        print("🟢 LOW COMPLEXITY - Good candidate for base branch")
    elif manifest['complexity_score'] < 100:
        print("🟡 MEDIUM COMPLEXITY - Acceptable but may need cleanup")
    else:
        print("🔴 HIGH COMPLEXITY - Consider this a rebuild target, not source")
    
    return manifest

def categorize_module(path):
    """Categorize a Python module based on its path."""
    path_str = str(path)
    if '/api/' in path_str:
        return 'api_endpoint'
    elif '/core/' in path_str:
        return 'core_business_logic'
    elif '/utils/' in path_str:
        return 'utility'
    elif '/models/' in path_str:
        return 'data_model'
    elif '/services/' in path_str:
        return 'service'
    elif 'test' in path_str:
        return 'test'
    else:
        return 'unknown'

def get_git_branch():
    """Get current git branch."""
    try:
        import subprocess
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except:
        return 'unknown'

def get_git_commit_hash():
    """Get current git commit hash."""
    try:
        import subprocess
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip()[:8] if result.returncode == 0 else 'unknown'
    except:
        return 'unknown'

def count_lines_of_code(file_path):
    """Count lines of code in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Filter out empty lines and comments
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            return len(code_lines)
    except:
        return 0

def calculate_architecture_quality(manifest):
    """Calculate architecture quality metrics."""
    quality = {
        "total_modules": len(manifest["existing_modules"]),
        "api_routes": len(manifest["api_routes"]),
        "test_coverage": len(manifest["test_files"]) / max(len(manifest["existing_modules"]), 1),
        "avg_file_size": sum(m["size"] for m in manifest["existing_modules"].values()) / max(len(manifest["existing_modules"]), 1),
        "redundancy_indicators": []
    }
    
    # Check for potential redundancy
    module_names = list(manifest["existing_modules"].keys())
    for name in module_names:
        similar_names = [n for n in module_names if n != name and (name in n or n in name)]
        if similar_names:
            quality["redundancy_indicators"].append({"base": name, "similar": similar_names})
    
    # Check for bloated files (>5KB for Python files is potentially bloated)
    quality["large_files"] = [
        {"name": name, "size": info["size"]} 
        for name, info in manifest["existing_modules"].items() 
        if info["size"] > 5000
    ]
    
    return quality

def calculate_complexity_score(manifest):
    """Calculate a complexity score for the codebase."""
    score = 0
    
    # Base score from number of modules
    score += len(manifest["existing_modules"]) * 1
    
    # Penalty for large files
    for module in manifest["existing_modules"].values():
        if module["size"] > 10000:  # 10KB+
            score += 5
        elif module["size"] > 5000:  # 5KB+
            score += 2
    
    # Penalty for potential redundancy
    if "architecture_quality" in manifest:
        score += len(manifest["architecture_quality"].get("redundancy_indicators", [])) * 3
    
    return score

def get_recent_changes():
    """Get recent git changes."""
    try:
        import subprocess
        result = subprocess.run(['git', 'log', '--oneline', '-10'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        return []
    except:
        return []

if __name__ == "__main__":
    create_session_manifest()
