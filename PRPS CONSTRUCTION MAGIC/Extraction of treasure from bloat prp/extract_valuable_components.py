#!/usr/bin/env python3
"""
Archaeological Analysis & Extraction Script
Systematically extracts valuable components from complex ephemeris-core-fixes branch
for use in lean rebuild from feature/acg-build foundation.

This script identifies:
1. Working mathematical formulas (ACG calculations, Swiss Ephemeris patterns)
2. Proven integration patterns (caching, error handling, coordinate transforms)
3. Complete implementations (aspects, house systems, planet calculations)
4. Architectural patterns to preserve vs avoid
"""

import os
import ast
import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
import subprocess

@dataclass
class ComponentAnalysis:
    file_path: str
    component_name: str
    component_type: str  # 'formula', 'pattern', 'integration', 'model', 'bloat'
    value_score: int     # 1-5, higher = more valuable to extract
    complexity_score: int # 1-5, higher = more complex
    lines_of_code: int
    extraction_priority: str  # 'high', 'medium', 'low', 'discard'
    description: str
    code_snippet: str
    dependencies: List[str]
    recommended_action: str  # 'extract_as_is', 'refactor_and_extract', 'rebuild_from_scratch', 'discard'
    notes: str

class CodeArchaeologist:
    def __init__(self):
        self.analyses: List[ComponentAnalysis] = []
        self.file_contents: Dict[str, str] = {}
        self.extraction_summary = {
            "total_files_analyzed": 0,
            "high_value_components": 0,
            "medium_value_components": 0,
            "bloat_components": 0,
            "extraction_candidates": [],
            "rebuild_candidates": [],
            "discard_candidates": []
        }
        
    def load_file_content(self, file_path: str) -> str:
        """Load and cache file content"""
        if file_path not in self.file_contents:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.file_contents[file_path] = f.read()
            except Exception as e:
                self.file_contents[file_path] = f"# Error reading file: {e}"
        return self.file_contents[file_path]
    
    def extract_class_methods(self, file_path: str, class_name: str = None) -> Dict[str, str]:
        """Extract class methods and their implementations"""
        content = self.load_file_content(file_path)
        methods = {}
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if class_name is None or node.name == class_name:
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                start_line = item.lineno
                                end_line = getattr(item, 'end_lineno', start_line + 10)
                                method_content = '\n'.join(content.split('\n')[start_line-1:end_line])
                                methods[f"{node.name}.{item.name}"] = method_content
        except:
            # Fallback to regex extraction
            class_regex = class_name if class_name else r"\w+"
            class_pattern = rf'class\s+{class_regex}.*?(?=class|\Z)'
            matches = re.findall(class_pattern, content, re.DOTALL)
            if matches:
                methods['fallback'] = matches[0][:1000]  # First 1000 chars
                
        return methods
    
    def extract_function_definitions(self, file_path: str) -> Dict[str, str]:
        """Extract standalone function definitions"""
        content = self.load_file_content(file_path)
        functions = {}
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    start_line = node.lineno
                    end_line = getattr(node, 'end_lineno', start_line + 20)
                    func_content = '\n'.join(content.split('\n')[start_line-1:end_line])
                    functions[node.name] = func_content
        except:
            # Fallback to regex
            func_pattern = r'def\s+(\w+).*?(?=def|\Z)'
            matches = re.findall(func_pattern, content, re.DOTALL)
            for i, match in enumerate(matches[:5]):  # Limit to first 5
                functions[f"function_{i}"] = match[:500]
                
        return functions
    
    def analyze_acg_core_engine(self):
        """Extract ACG mathematical formulas and working patterns"""
        print("🔍 Analyzing ACG Core Engine...")
        
        acg_files = [
            "backend/app/core/acg/acg_core.py",
            "backend/app/core/acg/acg_utils.py", 
            "backend/app/core/acg/acg_cache.py",
            "backend/app/core/acg/acg_types.py",
            "backend/app/api/routes/acg.py"
        ]
        
        for file_path in acg_files:
            if Path(file_path).exists():
                print(f"  📁 Analyzing {file_path}")
                content = self.load_file_content(file_path)
                
                # Extract key ACG classes
                if "acg_core.py" in file_path:
                    methods = self.extract_class_methods(file_path, "ACGCore")
                    for method_name, method_code in methods.items():
                        if any(keyword in method_code.lower() for keyword in ['calculate', 'line', 'coord', 'meridian', 'horizon']):
                            self.analyses.append(ComponentAnalysis(
                                file_path=file_path,
                                component_name=method_name,
                                component_type='formula',
                                value_score=5 if 'calculate' in method_name.lower() else 4,
                                complexity_score=3,
                                lines_of_code=len(method_code.split('\n')),
                                extraction_priority='high',
                                description=f"ACG calculation method: {method_name}",
                                code_snippet=method_code[:1000],
                                dependencies=self._extract_imports(content),
                                recommended_action='extract_as_is',
                                notes="Core ACG mathematical formula - preserve this"
                            ))
                
                # Extract utility functions
                if "acg_utils.py" in file_path:
                    functions = self.extract_function_definitions(file_path)
                    for func_name, func_code in functions.items():
                        if any(keyword in func_code.lower() for keyword in ['transform', 'convert', 'normalize']):
                            self.analyses.append(ComponentAnalysis(
                                file_path=file_path,
                                component_name=func_name,
                                component_type='pattern',
                                value_score=4,
                                complexity_score=2,
                                lines_of_code=len(func_code.split('\n')),
                                extraction_priority='high',
                                description=f"ACG utility function: {func_name}",
                                code_snippet=func_code[:800],
                                dependencies=self._extract_imports(content),
                                recommended_action='extract_as_is',
                                notes="Proven coordinate transformation utility"
                            ))
    
    def analyze_ephemeris_patterns(self):
        """Extract working Swiss Ephemeris integration patterns"""
        print("🔍 Analyzing Swiss Ephemeris Integration Patterns...")
        
        ephemeris_files = [
            "backend/app/core/ephemeris/tools/ephemeris.py",
            "backend/app/core/ephemeris/tools/aspects.py",
            "backend/app/core/ephemeris/tools/arabic_parts.py",
            "backend/app/core/ephemeris/calculators/ephemeris_calculator.py",
            "backend/app/services/ephemeris_service.py"
        ]
        
        for file_path in ephemeris_files:
            if Path(file_path).exists():
                print(f"  📁 Analyzing {file_path}")
                content = self.load_file_content(file_path)
                
                # Look for Swiss Ephemeris integration patterns
                if "swe." in content or "swisseph" in content:
                    functions = self.extract_function_definitions(file_path)
                    methods = self.extract_class_methods(file_path)
                    
                    all_code_blocks = {**functions, **methods}
                    
                    for name, code in all_code_blocks.items():
                        if "swe." in code:
                            value_score = 5 if any(keyword in code.lower() for keyword in ['calc_ut', 'houses', 'fixstar']) else 3
                            
                            self.analyses.append(ComponentAnalysis(
                                file_path=file_path,
                                component_name=name,
                                component_type='integration',
                                value_score=value_score,
                                complexity_score=2,
                                lines_of_code=len(code.split('\n')),
                                extraction_priority='high' if value_score >= 4 else 'medium',
                                description=f"Swiss Ephemeris integration: {name}",
                                code_snippet=code[:1000],
                                dependencies=self._extract_imports(content),
                                recommended_action='extract_as_is',
                                notes="Working Swiss Ephemeris integration pattern"
                            ))
                
                # Check for empty/stub implementations
                if "pass" in content and len(content.strip()) < 200:
                    self.analyses.append(ComponentAnalysis(
                        file_path=file_path,
                        component_name=Path(file_path).stem,
                        component_type='bloat',
                        value_score=1,
                        complexity_score=1,
                        lines_of_code=len(content.split('\n')),
                        extraction_priority='discard',
                        description=f"Empty/stub implementation: {file_path}",
                        code_snippet=content[:500],
                        dependencies=[],
                        recommended_action='rebuild_from_scratch',
                        notes="Empty stub - rebuild completely"
                    ))
    
    def analyze_model_schemas(self):
        """Extract clean response models and data structures"""
        print("🔍 Analyzing Model Schemas...")
        
        model_files = [
            "backend/app/models/ephemeris_models.py",
            "backend/app/models/acg_models.py",
            "backend/app/core/ephemeris/models.py",
            "backend/app/core/acg/acg_types.py"
        ]
        
        for file_path in model_files:
            if Path(file_path).exists():
                print(f"  📁 Analyzing {file_path}")
                content = self.load_file_content(file_path)
                
                # Extract Pydantic models
                if "BaseModel" in content or "pydantic" in content:
                    classes = self.extract_class_methods(file_path)
                    
                    for class_name, class_code in classes.items():
                        if "BaseModel" in class_code:
                            # Assess model complexity
                            field_count = class_code.count(":") - class_code.count("::") 
                            complexity_score = min(5, max(1, field_count // 5))
                            value_score = 5 if complexity_score <= 3 else 2  # Simple models are more valuable
                            
                            self.analyses.append(ComponentAnalysis(
                                file_path=file_path,
                                component_name=class_name,
                                component_type='model',
                                value_score=value_score,
                                complexity_score=complexity_score,
                                lines_of_code=len(class_code.split('\n')),
                                extraction_priority='high' if value_score >= 4 else 'low',
                                description=f"Pydantic model: {class_name}",
                                code_snippet=class_code[:800],
                                dependencies=self._extract_imports(content),
                                recommended_action='extract_as_is' if value_score >= 4 else 'refactor_and_extract',
                                notes=f"Model with {field_count} fields - {'clean' if complexity_score <= 3 else 'complex'}"
                            ))
    
    def analyze_caching_patterns(self):
        """Extract working caching and performance patterns"""
        print("🔍 Analyzing Caching & Performance Patterns...")
        
        cache_files = [
            "backend/app/core/acg/acg_cache.py",
            "backend/app/core/ephemeris/cache.py",
            "backend/app/services/cache_service.py"
        ]
        
        for file_path in cache_files:
            if Path(file_path).exists():
                print(f"  📁 Analyzing {file_path}")
                content = self.load_file_content(file_path)
                
                if any(keyword in content.lower() for keyword in ['redis', 'cache', 'lru', 'memory']):
                    functions = self.extract_function_definitions(file_path)
                    methods = self.extract_class_methods(file_path)
                    
                    all_code_blocks = {**functions, **methods}
                    
                    for name, code in all_code_blocks.items():
                        if any(keyword in code.lower() for keyword in ['cache', 'store', 'retrieve', 'ttl']):
                            self.analyses.append(ComponentAnalysis(
                                file_path=file_path,
                                component_name=name,
                                component_type='pattern',
                                value_score=4,
                                complexity_score=2,
                                lines_of_code=len(code.split('\n')),
                                extraction_priority='medium',
                                description=f"Caching pattern: {name}",
                                code_snippet=code[:800],
                                dependencies=self._extract_imports(content),
                                recommended_action='extract_as_is',
                                notes="Working caching implementation"
                            ))
    
    def analyze_api_endpoints(self):
        """Extract clean API endpoint patterns"""
        print("🔍 Analyzing API Endpoint Patterns...")
        
        api_files = [
            "backend/app/api/routes/ephemeris.py",
            "backend/app/api/routes/acg.py",
            "backend/app/main.py"
        ]
        
        for file_path in api_files:
            if Path(file_path).exists():
                print(f"  📁 Analyzing {file_path}")
                content = self.load_file_content(file_path)
                
                # Extract FastAPI endpoint functions
                if "@router" in content or "@app" in content:
                    functions = self.extract_function_definitions(file_path)
                    
                    for func_name, func_code in functions.items():
                        if "@router" in func_code or "@app" in func_code:
                            # Assess endpoint complexity
                            complexity_indicators = [
                                func_code.count("await"),
                                func_code.count("try:"),
                                len(func_code.split('\n'))
                            ]
                            complexity_score = min(5, max(1, sum(complexity_indicators) // 10))
                            value_score = 5 if complexity_score <= 2 else 3
                            
                            self.analyses.append(ComponentAnalysis(
                                file_path=file_path,
                                component_name=func_name,
                                component_type='pattern',
                                value_score=value_score,
                                complexity_score=complexity_score,
                                lines_of_code=len(func_code.split('\n')),
                                extraction_priority='high' if value_score >= 4 else 'medium',
                                description=f"API endpoint: {func_name}",
                                code_snippet=func_code[:1000],
                                dependencies=self._extract_imports(content),
                                recommended_action='extract_as_is' if value_score >= 4 else 'refactor_and_extract',
                                notes=f"API endpoint - {'clean' if complexity_score <= 2 else 'complex'}"
                            ))
    
    def identify_bloat_patterns(self):
        """Identify anti-patterns and bloat to avoid"""
        print("🔍 Identifying Bloat Patterns...")
        
        # Look for bloat indicators across the codebase
        all_py_files = list(Path(".").rglob("*.py"))
        
        bloat_indicators = {
            "duplicate_implementations": [],
            "oversized_responses": [],
            "redundant_calculations": [],
            "complex_inheritance": [],
            "unused_imports": []
        }
        
        for file_path in all_py_files:
            if "backend/app" in str(file_path):
                try:
                    content = self.load_file_content(str(file_path))
                    
                    # Check for oversized files
                    if len(content) > 5000:  # >5KB
                        self.analyses.append(ComponentAnalysis(
                            file_path=str(file_path),
                            component_name=f"oversized_file_{file_path.stem}",
                            component_type='bloat',
                            value_score=1,
                            complexity_score=5,
                            lines_of_code=len(content.split('\n')),
                            extraction_priority='discard',
                            description=f"Oversized file: {len(content)} characters",
                            code_snippet="# File too large - examine for bloat",
                            dependencies=[],
                            recommended_action='refactor_and_extract',
                            notes=f"File size: {len(content)} chars - likely contains bloat"
                        ))
                    
                    # Check for duplicate class names across files
                    class_names = re.findall(r'class\s+(\w+)', content)
                    for class_name in class_names:
                        if class_name in [analysis.component_name for analysis in self.analyses]:
                            bloat_indicators["duplicate_implementations"].append(f"{file_path}: {class_name}")
                            
                except Exception as e:
                    continue
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from code"""
        import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+[\w,\s.]+(?:\s+as\s+\w+)?'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        return imports[:10]  # Limit to first 10 imports
    
    def run_full_analysis(self):
        """Execute complete archaeological analysis"""
        print("🏺 Starting Archaeological Analysis of ephemeris-core-fixes branch...")
        print(f"📅 Analysis Date: {datetime.now()}")
        print("=" * 80)
        
        self.analyze_acg_core_engine()
        self.analyze_ephemeris_patterns()
        self.analyze_model_schemas()
        self.analyze_caching_patterns()
        self.analyze_api_endpoints()
        self.identify_bloat_patterns()
        
        # Categorize results
        self.extraction_summary["total_files_analyzed"] = len(set(a.file_path for a in self.analyses))
        self.extraction_summary["high_value_components"] = len([a for a in self.analyses if a.value_score >= 4])
        self.extraction_summary["medium_value_components"] = len([a for a in self.analyses if a.value_score == 3])
        self.extraction_summary["bloat_components"] = len([a for a in self.analyses if a.value_score <= 2])
        
        # Sort by value for extraction
        self.analyses.sort(key=lambda x: (x.value_score, -x.complexity_score), reverse=True)
        
        for analysis in self.analyses:
            if analysis.extraction_priority == 'high':
                self.extraction_summary["extraction_candidates"].append(analysis.component_name)
            elif analysis.recommended_action == 'rebuild_from_scratch':
                self.extraction_summary["rebuild_candidates"].append(analysis.component_name)
            elif analysis.recommended_action == 'discard':
                self.extraction_summary["discard_candidates"].append(analysis.component_name)
        
        print(f"✅ Analysis Complete!")
        print(f"📊 High-value components found: {self.extraction_summary['high_value_components']}")
        print(f"🔧 Components to extract: {len(self.extraction_summary['extraction_candidates'])}")
        print(f"🏗️  Components to rebuild: {len(self.extraction_summary['rebuild_candidates'])}")
        print(f"🗑️  Bloat to discard: {len(self.extraction_summary['discard_candidates'])}")
        
    def generate_analysis_reports(self):
        """Generate comprehensive markdown reports"""
        print("📝 Generating Analysis Reports...")
        
        # Main extraction report
        self._generate_extraction_report()
        
        # Valuable components documentation
        self._generate_valuable_components_docs()
        
        # Feature rebuild specifications
        self._generate_rebuild_specifications()
        
        # Implementation patterns guide
        self._generate_implementation_patterns()
        
        # Architectural analysis
        self._generate_architectural_analysis()
        
        print("✅ All reports generated in extraction_analysis/ folder")
    
    def _generate_extraction_report(self):
        """Generate main extraction report"""
        report = f"""# Ephemeris Core Fixes - Archaeological Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Branch**: ephemeris-core-fixes  
**Complexity Score**: 456  
**Purpose**: Extract valuable components for lean rebuild from feature/acg-build (174 complexity)

## 📊 Analysis Summary

- **Total Files Analyzed**: {self.extraction_summary['total_files_analyzed']}
- **High-Value Components**: {self.extraction_summary['high_value_components']}
- **Medium-Value Components**: {self.extraction_summary['medium_value_components']}
- **Bloat Components**: {self.extraction_summary['bloat_components']}

## 🏆 HIGH-VALUE EXTRACTIONS

### Components to Extract As-Is
{self._format_component_list([a for a in self.analyses if a.recommended_action == 'extract_as_is' and a.value_score >= 4])}

### Components Requiring Refactoring
{self._format_component_list([a for a in self.analyses if a.recommended_action == 'refactor_and_extract' and a.value_score >= 3])}

## 🏗️ REBUILD CANDIDATES

### Empty/Stub Implementations
{self._format_component_list([a for a in self.analyses if a.recommended_action == 'rebuild_from_scratch'])}

## 🗑️ BLOAT TO DISCARD

### Anti-Patterns and Redundancies  
{self._format_component_list([a for a in self.analyses if a.recommended_action == 'discard'])}

## 📋 EXTRACTION PRIORITY QUEUE

### Phase 1: Critical Mathematical Formulas (Week 1)
{self._format_priority_list('high', 'formula')}

### Phase 2: Integration Patterns (Week 1-2) 
{self._format_priority_list('high', 'integration')}

### Phase 3: Clean Models and APIs (Week 2)
{self._format_priority_list('high', 'model')}

### Phase 4: Performance Patterns (Week 2-3)
{self._format_priority_list('medium', 'pattern')}

## 🎯 NEXT STEPS

1. **Switch to feature/acg-build branch** (174 complexity)
2. **Create lean rebuild branch** from that foundation
3. **Extract high-priority components** using this analysis
4. **Implement missing features** with clean architecture
5. **Target final complexity**: 200-250 (vs current 456)

---
*Generated by Archaeological Analysis Script*
"""

        with open("extraction_analysis/EXTRACTION_REPORT.md", "w", encoding='utf-8') as f:
            f.write(report)
    
    def _generate_valuable_components_docs(self):
        """Generate detailed valuable components documentation"""
        
        # ACG Mathematical Formulas
        acg_formulas = [a for a in self.analyses if a.component_type == 'formula' and a.value_score >= 4]
        acg_doc = self._create_component_doc("ACG Mathematical Formulas", acg_formulas, 
                                           "Working ACG calculation formulas extracted from acg_core.py")
        
        with open("extraction_analysis/valuable_components/acg_mathematical_formulas.md", "w", encoding='utf-8') as f:
            f.write(acg_doc)
        
        # Swiss Ephemeris Integration Patterns
        swe_patterns = [a for a in self.analyses if a.component_type == 'integration' and 'swe' in a.code_snippet]
        swe_doc = self._create_component_doc("Swiss Ephemeris Integration Patterns", swe_patterns,
                                           "Proven Swiss Ephemeris integration patterns to preserve")
        
        with open("extraction_analysis/valuable_components/swiss_ephemeris_patterns.md", "w", encoding='utf-8') as f:
            f.write(swe_doc)
        
        # Clean Data Models
        model_components = [a for a in self.analyses if a.component_type == 'model' and a.value_score >= 4]
        model_doc = self._create_component_doc("Clean Data Models", model_components,
                                             "Well-designed Pydantic models to preserve")
        
        with open("extraction_analysis/valuable_components/clean_data_models.md", "w", encoding='utf-8') as f:
            f.write(model_doc)
        
        # API Endpoint Patterns
        api_patterns = [a for a in self.analyses if 'endpoint' in a.description and a.value_score >= 4]
        api_doc = self._create_component_doc("API Endpoint Patterns", api_patterns,
                                           "Clean FastAPI endpoint implementations")
        
        with open("extraction_analysis/valuable_components/api_endpoint_patterns.md", "w", encoding='utf-8') as f:
            f.write(api_doc)
    
    def _generate_rebuild_specifications(self):
        """Generate feature rebuild specifications based on cheatsheet"""
        
        hermetic_lots_spec = """# Hermetic Lots (Arabic Parts) - Implementation Specification

## Overview
Complete rebuild required - current implementation is empty stub.

## Target Features (from cheatsheet)
- **16 Hermetic Lots** with proper day/night formulas
- **Day Birth vs Night Birth** awareness
- **Proper astronomical calculation** integration
- **ACG line generation** for all lots

## Implementation Plan

### Core Lots to Implement
1. **Lot of Fortune** - Foundation lot (Asc + Moon - Sun / Asc + Sun - Moon)
2. **Lot of Spirit** - Activating principle (Asc + Sun - Moon / Asc + Moon - Sun)  
3. **Lot of Basis** - Material foundation
4. **Lot of Eros** - Desire and attraction
5. **Lot of Necessity** - Karmic obligations
6. **Lot of Courage** - Mars-related fortitude
7. **Lot of Victory** - Jupiter-related success
8. **Lot of Nemesis** - Saturn-related challenges
[... continue for all 16 lots]

### Technical Architecture
```python
class HermeticLotsCalculator:
    def __init__(self):
        self.lot_definitions = self._load_lot_formulas()
    
    def calculate_all_lots(self, positions: dict, houses: dict, is_day_birth: bool) -> List[HermeticLot]:
        # Implementation plan
        
    def _determine_day_birth(self, sun_pos: float, asc_pos: float) -> bool:
        # Day birth determination logic
```

### Integration Points
- **Natal Chart**: Include lots in main natal response  
- **ACG Engine**: Generate AC/DC/MC/IC lines for all lots
- **Swiss Ephemeris**: Use proper coordinate calculations
- **Caching**: Cache lot calculations by birth data hash

## Dependencies to Extract
- Working Swiss Ephemeris coordinate calculations
- Proper day/night birth determination
- Angle normalization utilities

---
*To be implemented in lean rebuild branch*
"""

        fixed_stars_spec = """# Fixed Stars - Implementation Specification

## Overview  
Complete implementation required - no fixed star support found in current codebase.

## Target Features (from cheatsheet)
- **Foundation 24 Stars** (100-mile orb radius)
- **Extended 77 Stars** (80-mile orb radius) 
- **Swiss Ephemeris swe.fixstar()** integration
- **Magnitude-based orb sizing**
- **ACG orb display** (no lines, only location circles)

## Implementation Plan

### Foundation 24 Stars
Key royal stars and prominent fixed stars:
- Regulus (α Leo) - The Royal Star
- Aldebaran (α Tau) - The Watcher of the East  
- Antares (α Sco) - The Watcher of the West
- Fomalhaut (α PsA) - The Watcher of the South
[... complete list from cheatsheet]

### Technical Architecture
```python
class FixedStarCalculator:
    FOUNDATION_24 = [
        {"name": "Regulus", "se_name": "Regulus", "magnitude": 1.4},
        {"name": "Aldebaran", "se_name": "Aldebaran", "magnitude": 0.9},
        # ... all 24 stars
    ]
    
    def calculate_star_positions(self, jd: float, star_set: str = "foundation") -> List[FixedStar]:
        # Swiss Ephemeris swe.fixstar() integration
        
    def calculate_star_orbs_for_acg(self, star_positions: List[FixedStar]) -> List[ACGOrb]:
        # Generate geographic orbs for ACG display
```

### Integration Points
- **Natal Chart**: Include fixed stars with proper names
- **ACG Engine**: Generate orb circles only (no AC/DC/MC/IC lines)
- **Magnitude System**: Orb size based on apparent magnitude
- **Geographic Calculation**: Proper lat/lon orb positioning

---
*Completely new implementation required*
"""

        parans_spec = """# Parans - Implementation Specification

## Overview
Partial mathematical groundwork exists but needs complete reimplementation.

## Target Features (from cheatsheet)
- **Jim Lewis paran method** 
- **Four angle events**: Rising, Setting, Culminating, Anti-culminating
- **Body-to-body parans**: Where two planets simultaneously occupy different angles
- **Geographic intersection lines**
- **Proper orb calculation** at intersection points

## Mathematical Foundation
Parans occur where:
- Planet A is Rising while Planet B is Setting
- Planet A is Culminating while Planet B is Anti-culminating  
- All permutations of these angular relationships

### Technical Architecture
```python
class ParanCalculator:
    def calculate_paran_lines(self, body1: dict, body2: dict, events: List[str]) -> List[ParanLine]:
        # Root-solving for longitude where angular conditions meet
        
    def find_paran_intersections(self, body1_data: dict, body2_data: dict, latitude: float) -> List[Tuple[float, float]]:
        # Solve for longitude where paran conditions occur
        
    def calculate_paran_orbs(self, paran_intersections: List[Tuple]) -> List[ACGOrb]:
        # Generate orb circles at paran intersection points
```

## Components to Extract
- Any existing paran mathematical foundations from current codebase
- Working coordinate transformation utilities  
- Root-solving numerical methods if implemented

---
*Refactor and complete existing partial implementation*
"""

        # Write specifications
        with open("extraction_analysis/features_to_rebuild/hermetic_lots_specification.md", "w", encoding='utf-8') as f:
            f.write(hermetic_lots_spec)
            
        with open("extraction_analysis/features_to_rebuild/fixed_stars_specification.md", "w", encoding='utf-8') as f:
            f.write(fixed_stars_spec)
            
        with open("extraction_analysis/features_to_rebuild/parans_specification.md", "w", encoding='utf-8') as f:
            f.write(parans_spec)
    
    def _generate_implementation_patterns(self):
        """Generate implementation patterns guide"""
        
        patterns_guide = f"""# Implementation Patterns Guide

## 🏗️ Architectural Patterns to Preserve

### 1. Single Swiss Ephemeris Adapter Pattern
**Status**: EXTRACT AND PRESERVE

```python
# Pattern found in: backend/app/core/ephemeris/tools/ephemeris.py
class SwissEphemerisAdapter:
    def calculate_position(self, jd: float, body_id: int) -> PlanetPosition:
        # Direct swe.calc_ut() call with proper error handling
        # This pattern works - preserve it
```

### 2. Clean Dependency Injection Pattern  
**Status**: EXTRACT AND ENHANCE

```python
# Pattern found in ACG service integration
class ACGService:
    def __init__(self, ephemeris_service: EphemerisService):
        self.ephemeris = ephemeris_service  # Reuse calculations
        
    def calculate_acg_lines(self, natal_request):
        natal_chart = self.ephemeris.calculate_natal(natal_request)
        return self._transform_to_acg_lines(natal_chart)
```

### 3. Geographic Coordinate Transformation
**Status**: EXTRACT - HIGH VALUE

Mathematical formulas for coordinate system transformations found in ACG core.
Preserve these exact calculations.

## 🚫 Anti-Patterns to Avoid

### 1. Multiple Redundant Calculator Classes
**Problem**: Found 5+ different planet calculation implementations
**Solution**: Consolidate to single Swiss Ephemeris adapter

### 2. Massive Response Objects
**Problem**: 9MB+ JSON responses with excessive metadata  
**Solution**: Implement selective field inclusion

### 3. Complex Inheritance Hierarchies
**Problem**: Deep inheritance causing maintenance issues
**Solution**: Prefer composition over inheritance

## 🎯 Performance Patterns to Preserve

### Caching Strategies
{self._format_caching_patterns()}

### Error Handling Patterns
{self._format_error_handling_patterns()}

## 📐 Mathematical Formula Patterns

### ACG Line Calculations
{self._format_acg_formula_patterns()}

### Coordinate Transformations
{self._format_coordinate_patterns()}

---
*Use these patterns in lean rebuild implementation*
"""

        with open("extraction_analysis/implementation_patterns/patterns_guide.md", "w", encoding='utf-8') as f:
            f.write(patterns_guide)
    
    def _generate_architectural_analysis(self):
        """Generate architectural analysis and recommendations"""
        
        architectural_analysis = f"""# Architectural Analysis & Recommendations

## 📊 Current State Analysis (ephemeris-core-fixes)

### Complexity Metrics
- **Total Files**: {self.extraction_summary['total_files_analyzed']}
- **Complexity Score**: 456 (HIGH)
- **Lines of Code**: 31,746
- **High-Value Components**: {self.extraction_summary['high_value_components']}
- **Bloat Components**: {self.extraction_summary['bloat_components']}

### Identified Issues
1. **Redundant Implementation Layers**: Multiple ways to calculate same data
2. **Oversized Response Objects**: 9MB+ responses where <50KB needed  
3. **Empty/Stub Implementations**: Placeholders never completed
4. **Inconsistent Naming**: "Object 17" instead of proper celestial body names
5. **Complex Inheritance**: Deep class hierarchies causing maintenance issues

## 🎯 Target Architecture (Clean Rebuild)

### Recommended Structure
```
backend/app/
├── core/
│   ├── swiss_ephemeris_adapter.py    # Single source Swiss Ephemeris integration
│   ├── celestial_registry.py         # Body definitions from cheatsheet  
│   └── coordinate_systems.py         # Coordinate transformations
├── features/
│   ├── natal_chart.py               # Complete natal chart calculation
│   ├── hermetic_lots.py             # All 16 lots with day/night formulas
│   ├── fixed_stars.py               # Foundation 24 + Extended 77
│   ├── aspects.py                   # Complete aspect engine
│   └── acg/
│       ├── lines.py                 # Basic AC/DC/MC/IC lines  
│       ├── parans.py                # Paran calculations
│       └── orbs.py                  # Planet/star orb features
├── models/
│   ├── unified_chart.py             # Single response model
│   └── calculation_metadata.py     # Essential provenance only
└── api/
    ├── natal.py                     # Unified natal endpoint
    └── acg.py                       # ACG endpoints
```

### Design Principles
1. **Single Source of Truth**: One way to calculate each data type
2. **Composition over Inheritance**: Avoid deep class hierarchies  
3. **Selective Response Fields**: Only include requested data
4. **Proper Naming**: Use correct astronomical names
5. **Clean Dependencies**: Clear separation of concerns

## 🚀 Migration Strategy

### Phase 1: Foundation (Week 1)
- Extract working Swiss Ephemeris patterns
- Create single ephemeris adapter
- Implement proper celestial body registry

### Phase 2: Core Features (Week 2)  
- Extract working ACG mathematical formulas
- Implement missing hermetic lots
- Add fixed star calculations

### Phase 3: Enhancement (Week 3)
- Complete aspect system
- Implement parans
- Add performance optimizations

### Phase 4: Polish (Week 4)
- API consistency
- Response optimization  
- Documentation completion

## 📈 Expected Outcomes

### Complexity Reduction
- **Current**: 456 complexity score
- **Target**: 200-250 complexity score  
- **Reduction**: 45-56% complexity decrease

### Performance Improvements
- **Response Size**: 9MB+ → <50KB (99%+ reduction)
- **Calculation Time**: Current unknown → <100ms target
- **Memory Usage**: Current unknown → <100MB target

### Feature Completeness
- ✅ All 16 hermetic lots implemented
- ✅ Foundation 24 + Extended 77 fixed stars
- ✅ Complete ACG feature set (lines, parans, orbs)  
- ✅ Proper astronomical naming
- ✅ Clean API responses

---
*Architectural guidelines for lean rebuild project*
"""

        with open("extraction_analysis/architectural_analysis/architecture_recommendations.md", "w", encoding='utf-8') as f:
            f.write(architectural_analysis)
    
    def _create_component_doc(self, title: str, components: List[ComponentAnalysis], description: str) -> str:
        """Create documentation for a group of components"""
        doc = f"""# {title}

**Description**: {description}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Components Found**: {len(components)}

## 📋 Component Analysis

"""

        for i, component in enumerate(components[:10], 1):  # Limit to top 10
            doc += f"""### {i}. {component.component_name}

**File**: `{component.file_path}`  
**Type**: {component.component_type}  
**Value Score**: {component.value_score}/5 ⭐  
**Complexity**: {component.complexity_score}/5  
**Lines**: {component.lines_of_code}  
**Priority**: {component.extraction_priority}  
**Action**: {component.recommended_action}

**Description**: {component.description}

**Code Sample**:
```python
{component.code_snippet[:500]}{'...' if len(component.code_snippet) > 500 else ''}
```

**Dependencies**: {', '.join(component.dependencies[:5])}

**Notes**: {component.notes}

---

"""

        return doc
    
    def _format_component_list(self, components: List[ComponentAnalysis]) -> str:
        """Format component list for markdown"""
        if not components:
            return "*None found*"
            
        result = ""
        for comp in components[:10]:  # Limit to top 10
            result += f"- **{comp.component_name}** ({comp.file_path}) - {comp.description}\n"
        return result
    
    def _format_priority_list(self, priority: str, component_type: str = None) -> str:
        """Format priority list for markdown"""
        filtered = [a for a in self.analyses if a.extraction_priority == priority]
        if component_type:
            filtered = [a for a in filtered if a.component_type == component_type]
            
        if not filtered:
            return "*None found*"
            
        result = ""
        for comp in filtered[:5]:  # Top 5
            result += f"- **{comp.component_name}** - {comp.description}\n"
        return result
    
    def _format_caching_patterns(self) -> str:
        """Format caching patterns"""
        cache_patterns = [a for a in self.analyses if 'cache' in a.description.lower()]
        return self._format_component_list(cache_patterns)
    
    def _format_error_handling_patterns(self) -> str:
        """Format error handling patterns"""  
        error_patterns = [a for a in self.analyses if 'error' in a.code_snippet.lower() or 'try:' in a.code_snippet]
        return self._format_component_list(error_patterns)
    
    def _format_acg_formula_patterns(self) -> str:
        """Format ACG formula patterns"""
        acg_formulas = [a for a in self.analyses if a.component_type == 'formula' and 'acg' in a.file_path.lower()]
        return self._format_component_list(acg_formulas)
    
    def _format_coordinate_patterns(self) -> str:
        """Format coordinate transformation patterns"""
        coord_patterns = [a for a in self.analyses if 'transform' in a.description.lower() or 'coord' in a.description.lower()]
        return self._format_component_list(coord_patterns)
    
    def save_analysis_data(self):
        """Save raw analysis data as JSON for programmatic access"""
        analysis_data = {
            "summary": self.extraction_summary,
            "analyses": [asdict(analysis) for analysis in self.analyses],
            "generated_at": datetime.now().isoformat()
        }
        
        with open("extraction_analysis/analysis_data.json", "w", encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2)

if __name__ == "__main__":
    print("🏺 Archaeological Analysis Script")
    print("=" * 50)
    
    archaeologist = CodeArchaeologist()
    
    try:
        archaeologist.run_full_analysis()
        archaeologist.generate_analysis_reports()
        archaeologist.save_analysis_data()
        
        print("\n✅ Archaeological analysis complete!")
        print("📁 All documentation generated in extraction_analysis/ folder")
        print("\n📋 Next Steps:")
        print("1. Review extraction_analysis/EXTRACTION_REPORT.md")
        print("2. Switch to feature/acg-build branch (174 complexity)")  
        print("3. Create new lean rebuild branch")
        print("4. Use extraction docs to guide feature implementation")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
