# Meridian Ep### Quality Gates
Before any code integration, ensure:
- [ ] All tests pass (`pytest backend/tests/`)
- [ ] Performance benchmarks meet targets (`pytest backend/tests/benchmarks/`)
- [ ] API documentation is auto-generated and accurate
- [ ] Monitoring metrics are properly instrumented
- [ ] Error handling follows established patterns

## 🛑 MANDATORY PRE-MODIFICATION CHECKLIST

### Before Creating ANY New File:
1. **SEARCH FIRST**: Check if similar functionality exists
   ```bash
   # Search for similar files
   find . -name "*keyword*" -type f
   
   # Search for similar functionality
   grep -r "function_name" backend/ --include="*.py"
   
   # Check import usage
   grep -r "from.*import.*ClassName" backend/
   ```

2. **VERIFY NECESSITY**: Ask these questions:
   - [ ] Does this functionality already exist elsewhere?
   - [ ] Can I extend an existing module instead?
   - [ ] Is this solving a new problem or duplicating work?

3. **CHECK ACTIVE FILES**: Never create alternatives to active files
   ```bash
   # Check if file is actively used
   git log -n 5 --oneline -- path/to/file.py
   
   # Check if file has recent changes
   git diff HEAD~10 -- path/to/file.py
   ```

## 📁 FILE MODIFICATION RULES

### RULE 1: NEVER Create When You Can Modify
**❌ DON'T DO THIS:**
- Creating `new_fixed_stars.py` when `fixed_stars.py` exists
- Making `test_fixed_stars_v2.py` instead of updating `test_fixed_stars.py`
- Writing `working_solution.json` alongside existing data files

**✅ DO THIS INSTEAD:**
- Modify the existing file directly
- Use git branches for experimental changes
- Comment out old code with deprecation notes if needed

### RULE 2: Single Source of Truth
**For each domain, there must be ONLY ONE:**
- Implementation file (e.g., ONE fixed_stars.py)
- Test file (e.g., ONE test_fixed_stars.py)
- Configuration file (e.g., ONE redis_config.py)
- Data file (e.g., ONE fixed_stars_data.json)

### RULE 3: Location Hierarchy
```
NEVER place files in root that belong in:
├── backend/
│   ├── app/           <- Application code goes here
│   └── tests/         <- Test files go here
├── docs/              <- Documentation goes here
└── scripts/           <- Utility scripts go here

Root level is ONLY for:
- README.md
- docker-compose.yml
- .env.example
- requirements files
- configuration files (pyproject.toml, etc.)
```

## 🔄 INCREMENTAL MODIFICATION PROTOCOL

### When Improving Existing Features:

1. **Start with Git Status Check:**
   ```bash
   git status
   git diff
   # Ensure you know current state before changes
   ```

2. **Create a Feature Branch:**
   ```bash
   git checkout -b fix/specific-issue-name
   # Never work directly on main during iterations
   ```

3. **Modify in Place:**
   ```python
   # In existing file, mark your changes clearly:
   
   # TODO: [DATE] - Refactoring for performance improvement
   # Previous implementation kept for reference until tests pass
   
   def old_function():  # DEPRECATED: Remove after new version validated
       pass
   
   def function():  # ENHANCED: [What was improved]
       """Updated implementation with [specific improvements]."""
       pass
   ```

4. **Test Before Removing Old Code:**
   ```bash
   # Run tests with both implementations
   pytest tests/ -v
   
   # Only remove old code after validation
   ```

## 📊 PROJECT STATE AWARENESS

### Required Context Commands (Run Before Any Work):

```bash
# 1. Understand current structure
tree backend/app -L 2

# 2. Check recent changes
git log --oneline -20

# 3. Find TODO items and technical debt
grep -r "TODO\|FIXME\|HACK" backend/ --include="*.py"

# 4. Check test coverage
pytest --cov=backend/app backend/tests/

# 5. Identify large/complex files
find backend/ -name "*.py" -exec wc -l {} \; | sort -rn | head -20
```

## 🚫 ANTI-PATTERNS TO AVOID

### 1. The "Alternative Implementation" Anti-pattern
**❌ BAD:**
```python
# fixed_stars.py (original)
# fixed_stars_new.py (your "better" version)
# fixed_stars_optimized.py (another attempt)
# working_fixed_stars.py (the "working" one)
```

**✅ GOOD:**
```python
# fixed_stars.py (single, evolving implementation)
# With proper version control via git
```

### 2. The "Test Explosion" Anti-pattern
**❌ BAD:**
```
tests/
├── test_calculations.py
├── test_calculations_unit.py
├── test_calculations_integration.py
├── test_calculations_new.py
└── test_calculations_performance.py
```

**✅ GOOD:**
```
tests/
└── test_calculations.py  # Contains all test types, clearly organized
    ├── TestUnit
    ├── TestIntegration
    └── TestPerformance
```

### 3. The "Configuration Scatter" Anti-pattern
**❌ BAD:**
- Config in .env
- Config in config.py
- Config in settings.json
- Config hardcoded in files

**✅ GOOD:**
- Single configuration source
- Environment-specific overrides
- Clear configuration hierarchy

## 📝 COMMIT MESSAGE STANDARDS

### Use Conventional Commits:
```bash
# Format: <type>(<scope>): <subject>

feat(api): add batch calculation endpoint
fix(cache): resolve Redis connection timeout
refactor(fixed-stars): consolidate implementations
test(ephemeris): add performance benchmarks
docs(api): update endpoint documentation
chore(deps): update Swiss Ephemeris version

# Include in commit body:
- What changed
- Why it changed  
- What it affects
- Breaking changes (if any)
``` Development Guide for AI Agents

## 🎯 Project Philosophy & Standards

### Core Principles
- **Swiss Ephemeris as Gold Standard**: All astronomical calculations must use Swiss Ephemeris as the authoritative source
- **Performance-First Architecture**: Sub-100ms median response times, 10x batch processing improvements
- **Production-Ready Code**: Comprehensive error handling, monitoring integration, and validation
- **Backwards Compatibility**: Maintain API compatibility while adding new features
- **Test-Driven Development**: >90% test coverage with performance benchmarks
- **Single Source of Truth**: Never duplicate functionality - modify existing files instead of creating new ones
- **No Agentic Sprawl**: Follow strict file modification protocols to prevent code duplication

### Quality Gates
Before any code integration, ensure:
- [ ] All tests pass (`pytest backend/tests/`)
- [ ] Performance benchmarks meet targets (`pytest backend/tests/benchmarks/`)
- [ ] API documentation is auto-generated and accurate
- [ ] Monitoring metrics are properly instrumented
- [ ] Error handling follows established patterns

```

## 🎯 FEATURE IMPLEMENTATION DECISION TREE

### Decision Flow for New Features
```
New Feature Request
    ↓
Does similar functionality exist?
    ├── Yes → Extend existing module → Update existing tests
    └── No → Is it core business logic?
              ├── Yes → Add to backend/app/core/ → Create new module with tests
              └── No → Is it an API endpoint?
                        ├── Yes → Add to backend/app/api/routes/ → Create new module with tests  
                        └── No → Add to backend/app/utils/ → Create new module with tests
                        
All paths lead to → Run full test suite → Update documentation
```

## 🏗️ REFACTORING PROTOCOL

### When Cleaning Up Technical Debt:

1. **Document Current State:**
   ```python
   # Create a refactoring plan file
   # refactoring_plan_YYYYMMDD.md
   """
   ## Current Issues:
   - [Issue 1]: Files affected: [...]
   - [Issue 2]: Dependencies: [...]
   
   ## Proposed Changes:
   1. Step 1: [What and why]
   2. Step 2: [What and why]
   
   ## Risk Assessment:
   - Breaking changes: [...]
   - Rollback plan: [...]
   """
   ```

2. **Incremental Refactoring:**
   ```python
   # Phase 1: Add new implementation alongside old
   class LegacyCalculator:  # Mark as legacy
       """DEPRECATED: Use NewCalculator instead."""
       pass
   
   class NewCalculator:  # New implementation
       """Replacement for LegacyCalculator with [improvements]."""
       pass
   
   # Phase 2: Migrate usage gradually
   # Phase 3: Remove legacy code after validation
   ```

## 🔍 VALIDATION REQUIREMENTS

### Before EVERY commit:
```bash
# 1. Check you haven't created duplicates
find . -name "*.py" -newer .git/index

# 2. Verify no broken imports
python -c "import backend.app.main"

# 3. Run quick test suite
pytest backend/tests/ -x --ff

# 4. Check for unused files
git status --ignored

# 5. Verify documentation is updated
grep -r "TODO.*doc" backend/
```

## 🏗️ Architecture Overview

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │────│  Core Engine     │────│ Swiss Ephemeris │
│   (REST API)    │    │  (Calculations)  │    │  (Calculations) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       
         │              ┌──────────────────┐             
         └──────────────│  Redis Cache     │             
                        │  (Performance)   │             
                        └──────────────────┘             
                                 │                       
                        ┌──────────────────┐             
                        │  Prometheus      │             
                        │  (Monitoring)    │             
                        └──────────────────┘             
```

### Key Directories
- `backend/app/api/` - FastAPI routes and request/response models
- `backend/app/core/ephemeris/` - Core calculation engine
- `backend/app/core/performance/` - Performance optimizations
- `backend/app/core/monitoring/` - Metrics and monitoring
- `backend/tests/` - Test suites and benchmarks
- `docs/` - MkDocs documentation site

## 🚀 Development Patterns

### 1. Adding New API Endpoints

**Template Pattern:**
```python
from fastapi import APIRouter, HTTPException, status
from app.api.models.schemas import YourRequestModel, YourResponseModel
from app.core.monitoring.metrics import timed_calculation, get_metrics

router = APIRouter(prefix="/ephemeris", tags=["ephemeris"])

@router.post(
    "/your-endpoint", 
    response_model=YourResponseModel,
    summary="Brief description",
    description="Detailed description with examples"
)
@timed_calculation("your_calculation_type")
async def your_endpoint(request: YourRequestModel):
    """
    Calculate [description]
    
    Args:
        request: Your request model with validation
        
    Returns:
        YourResponseModel: Calculated results
        
    Raises:
        HTTPException: For validation or calculation errors
    """
    try:
        # Input validation
        validated_data = request.dict()
        
        # Perform calculation
        result = perform_your_calculation(validated_data)
        
        # Record metrics
        metrics = get_metrics()
        metrics.record_calculation("your_calculation_type", duration, True)
        
        return YourResponseModel(
            success=True,
            data=result,
            metadata={
                "calculation_type": "your_calculation_type",
                "processing_time_ms": duration * 1000
            }
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "validation_error", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "calculation_error", "message": "Calculation failed"}
        )
```

### 2. Core Calculation Pattern

**All calculations must follow this pattern:**
```python
from app.core.ephemeris.classes.cache import get_global_cache
from app.core.ephemeris.classes.redis_cache import get_redis_cache
from app.core.monitoring.metrics import timed_calculation

@timed_calculation("calculation_type")
def calculate_something(input_data: dict) -> dict:
    """
    Perform astrological calculation with caching and error handling.
    """
    # 1. Generate cache key
    cache_key = generate_cache_key(input_data)
    
    # 2. Try Redis cache first
    redis_cache = get_redis_cache()
    cached_result = redis_cache.get("calculation_type", input_data)
    if cached_result:
        return cached_result
    
    # 3. Try memory cache
    memory_cache = get_global_cache()
    cached_result = memory_cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # 4. Perform calculation using Swiss Ephemeris
    try:
        result = perform_swiss_ephemeris_calculation(input_data)
        
        # 5. Cache results
        memory_cache.put(cache_key, result, ttl=3600)
        redis_cache.set("calculation_type", input_data, result, ttl=3600)
        
        return result
        
    except Exception as e:
        logger.error(f"Swiss Ephemeris calculation failed: {e}")
        raise CalculationError(f"Failed to calculate: {e}")
```

### 3. Performance Optimization Requirements

**Batch Processing:**
```python
# Always implement batch versions for multiple calculations
def calculate_multiple_charts(requests: List[ChartRequest]) -> List[ChartResult]:
    """Use BatchCalculator for 10x+ performance improvement."""
    from app.core.ephemeris.tools.batch import BatchCalculator
    
    calculator = BatchCalculator()
    return calculator.calculate_batch_positions(requests)
```

**Memory Optimization:**
```python
# Use structure-of-arrays for large datasets
from app.core.performance.optimizations import MemoryOptimizations

def process_large_dataset(data: List[Dict]) -> Dict[str, np.ndarray]:
    return MemoryOptimizations.optimize_array_operations(data)
```

### 4. Error Handling Standards

**Use consistent error patterns:**
```python
from app.api.models.schemas import ErrorResponse

# Validation errors
raise HTTPException(
    status_code=422,
    detail={
        "success": False,
        "error": "validation_error",
        "message": "Request validation failed",
        "details": {"field": "specific_issue"}
    }
)

# Calculation errors
raise HTTPException(
    status_code=500,
    detail={
        "success": False,
        "error": "calculation_error", 
        "message": "Ephemeris calculation failed",
        "details": {"error_type": "swiss_ephemeris_error"}
    }
)

# Rate limiting
raise HTTPException(
    status_code=429,
    detail={
        "success": False,
        "error": "rate_limit_exceeded",
        "message": "Rate limit exceeded",
        "details": {"retry_after": 60}
    }
)
```

## 🧪 Testing Requirements

### 1. Unit Tests (Required)
```python
import pytest
from app.core.ephemeris.your_module import your_function

class TestYourModule:
    def test_valid_input(self):
        """Test with valid input data."""
        result = your_function(valid_input)
        assert result is not None
        assert result["success"] is True
    
    def test_invalid_input(self):
        """Test error handling with invalid input."""
        with pytest.raises(ValidationError):
            your_function(invalid_input)
    
    def test_edge_cases(self):
        """Test boundary conditions and edge cases."""
        # Test extreme coordinates, dates, etc.
        pass
```

### 2. Performance Benchmarks (Required)
```python
import pytest

class TestYourModulePerformance:
    @pytest.mark.benchmark(group="your_module")
    def test_calculation_performance(self, benchmark):
        """Benchmark must show reasonable performance."""
        result = benchmark(your_function, test_input)
        assert result is not None
    
    def test_batch_performance_improvement(self):
        """Batch operations must be 5x+ faster."""
        # Test individual vs batch processing
        individual_time = time_individual_processing()
        batch_time = time_batch_processing()
        
        improvement = individual_time / batch_time
        assert improvement >= 5.0  # Minimum 5x improvement
```

### 3. Integration Tests (Required for API endpoints)
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_your_endpoint():
    """Test complete API workflow."""
    response = client.post("/ephemeris/your-endpoint", json=test_data)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "data" in response.json()
```

## 📊 Monitoring Integration

### Required Metrics
Every new feature must include metrics:

```python
from app.core.monitoring.metrics import get_metrics

# Record all calculations
metrics = get_metrics()
metrics.record_calculation("calculation_type", duration, success)

# Record API operations  
metrics.record_api_request(method, endpoint, status_code, duration)

# Record cache operations
metrics.record_cache_operation(operation, cache_type, result)

# Update system health
metrics.update_system_health("component_name", healthy)
```

## 🔄 Data Models & Schemas

### Pydantic Model Standards
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Union, List
from datetime import datetime

class YourRequestModel(BaseModel):
    """
    Request model with comprehensive validation.
    
    Example:
        {
            "name": "John Doe",
            "datetime": {"iso_string": "2000-01-01T12:00:00"},
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060}
        }
    """
    name: str = Field(..., description="Subject name", example="John Doe")
    datetime: DateTimeInput = Field(..., description="Birth datetime")
    coordinates: CoordinateInput = Field(..., description="Birth coordinates")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class YourResponseModel(BaseModel):
    """Response model with complete data structure."""
    success: bool = Field(..., description="Request success status")
    data: Optional[dict] = Field(None, description="Calculation results")
    metadata: Optional[dict] = Field(None, description="Processing metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {"result": "calculation_data"},
                "metadata": {"processing_time_ms": 45.2}
            }
        }
```

## 🚨 Critical Requirements

### Before Submitting Any Code:

1. **Performance Validation**
   ```bash
   # Run performance validation
   python scripts/validate-performance.py
   ```

2. **Complete Test Suite**
   ```bash
   # All tests must pass
   cd backend && python -m pytest tests/ -v
   
   # Benchmarks must meet targets
   python -m pytest tests/benchmarks/ --benchmark-only
   ```

3. **API Documentation**
   ```bash
   # Generate updated API docs
   python scripts/build-docs.py
   ```

4. **Code Quality**
   ```bash
   # Linting and formatting
   ruff check backend/
   ruff format backend/
   
   # Type checking
   mypy backend/app/
   ```

## 🛡️ PREVENTION MECHANISMS

### Automated Pre-Commit Checks
Create these validation scripts to prevent duplication:

```python
# scripts/pre-commit-check.py
"""Run before allowing commits."""

import os
import sys
from pathlib import Path

def check_for_duplicates():
    """Prevent duplicate file creation."""
    files = {}
    for path in Path('backend').rglob('*.py'):
        basename = path.stem
        if basename in files:
            print(f"❌ Duplicate detected: {path} and {files[basename]}")
            return False
        files[basename] = path
    return True

def check_file_locations():
    """Ensure files are in correct directories."""
    root_tests = list(Path('.').glob('test_*.py'))
    if root_tests:
        print(f"❌ Test files in root: {root_tests}")
        print("   Move them to backend/tests/")
        return False
    
    root_data = list(Path('.').glob('*.json'))
    large_root_data = [f for f in root_data if f.stat().st_size > 1000]
    if large_root_data:
        print(f"❌ Data files in root: {large_root_data}")
        print("   Move them to backend/data/")
        return False
    
    return True

def check_for_temp_files():
    """Find temporary or working files that shouldn't be committed."""
    temp_patterns = ['*temp*', '*working*', '*backup*', '*old*', '*new*']
    temp_files = []
    
    for pattern in temp_patterns:
        temp_files.extend(Path('.').rglob(pattern))
    
    if temp_files:
        print(f"❌ Temporary files detected: {temp_files}")
        print("   Remove or rename these files")
        return False
    
    return True

if __name__ == "__main__":
    checks = [
        check_for_duplicates(),
        check_file_locations(),
        check_for_temp_files(),
    ]
    
    if not all(checks):
        print("\n❌ Pre-commit checks failed!")
        sys.exit(1)
    else:
        print("✅ All pre-commit checks passed!")
```

### Project State Manifest Generator
```python
# scripts/generate-manifest.py
"""Create manifest of current project state for AI reference."""

import os
import json
from pathlib import Path
from datetime import datetime

def create_session_manifest():
    """Create a manifest of current state for AI reference."""
    
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "existing_modules": {},
        "test_files": [],
        "data_files": [],
        "config_files": [],
        "recent_changes": [],
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
        }
    }
    
    # Map all Python modules
    for path in Path('backend/app').rglob('*.py'):
        if path.name != '__init__.py':
            module_name = path.stem
            manifest["existing_modules"][module_name] = {
                "path": str(path),
                "size": path.stat().st_size,
                "purpose": "core_module"
            }
    
    # Map test files
    for path in Path('backend/tests').rglob('test_*.py'):
        manifest["test_files"].append({
            "name": path.stem,
            "path": str(path),
            "size": path.stat().st_size
        })
    
    # Map data files
    for ext in ['.json', '.yaml', '.csv']:
        for path in Path('.').rglob(f'*{ext}'):
            if path.stat().st_size > 100:  # Only significant files
                manifest["data_files"].append({
                    "name": path.name,
                    "path": str(path),
                    "size": path.stat().st_size
                })
    
    # Save manifest
    with open('.agentic-manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Manifest created: .agentic-manifest.json")
    print(f"📁 Tracked {len(manifest['existing_modules'])} modules")
    print(f"🧪 Found {len(manifest['test_files'])} test files")
    print(f"📊 Found {len(manifest['data_files'])} data files")
    
    return manifest

if __name__ == "__main__":
    create_session_manifest()
```

### GitHub Recovery Strategy
```bash
# scripts/git-recovery.sh
#!/bin/bash

echo "🔄 GitHub Recovery & Cleanup Strategy"

# 1. Create backup of current state
git checkout -b "backup/pre-cleanup-$(date +%Y%m%d)" 2>/dev/null
git add -A
git commit -m "backup: current state before cleanup" 2>/dev/null

# 2. Find last stable commit
echo "📊 Recent commits:"
git log --oneline --graph -10

# 3. Interactive selection of good commits
echo "🎯 Use this to create clean branch:"
echo "git checkout -b cleanup/consolidated main"
echo "git cherry-pick <good-commit-hashes>"

# 4. Identify duplicate files for cleanup
echo "🔍 Potential duplicates found:"
find . -name "*.py" -exec basename {} \; | sort | uniq -d
find . -name "*.json" -size +1000c -exec basename {} \; | sort | uniq -d
```

## 🎯 Performance Targets (Non-Negotiable)

- **API Response Time**: <100ms median for all endpoints
- **Batch Performance**: 5x+ improvement over individual processing
- **Cache Hit Rate**: >70% under realistic load
- **Memory Efficiency**: <1MB per calculation
- **Test Coverage**: >90% for all new code
- **Error Rate**: <1% under normal load

## 📋 Common Pitfalls to Avoid

1. **Don't bypass caching** - Always implement Redis + memory caching
2. **Don't ignore error handling** - Follow established error patterns
3. **Don't skip performance tests** - Benchmark every calculation
4. **Don't break backwards compatibility** - Maintain existing API contracts
5. **Don't forget monitoring** - Instrument all new functionality
6. **Don't hardcode values** - Use configuration and environment variables
7. **Don't create duplicate files** - Always modify existing implementations
8. **Don't place files in wrong directories** - Follow strict location hierarchy
9. **Don't create "new", "temp", or "working" files** - Use git branches for experiments
10. **Don't skip the pre-modification checklist** - Search before creating anything

## 🔗 Key Files to Study

**Before implementing new features, review:**
- `backend/app/api/routes/ephemeris.py` - API pattern examples
- `backend/app/core/ephemeris/charts/natal.py` - Calculation patterns
- `backend/app/core/monitoring/metrics.py` - Monitoring integration
- `backend/tests/api/routes/test_ephemeris.py` - Testing patterns
- `backend/app/core/performance/optimizations.py` - Performance patterns

## 🆘 Getting Help

When in doubt:
1. **Search before creating** - Check for existing implementations first
2. **Follow existing patterns** in the codebase
3. **Maintain performance standards** - never compromise on speed
4. **Test comprehensively** - unit, integration, and performance tests
5. **Document thoroughly** - update API docs and examples
6. **Monitor everything** - add metrics for observability
7. **Use the pre-modification checklist** - Prevent duplication from the start
8. **Generate project manifest** - Run `python scripts/generate-manifest.py` before major changes

### Emergency Recovery Protocol
If you've already created duplicate files or messy structure:
1. **Stop immediately** - Don't create more files
2. **Run pre-commit checks** - `python scripts/pre-commit-check.py`
3. **Create backup branch** - Preserve current work
4. **Follow git recovery strategy** - Use the provided recovery scripts
5. **Consolidate systematically** - Fix one domain at a time

Remember: The goal is to maintain the high performance and reliability standards while adding powerful new capabilities to the Meridian Ephemeris system - **WITHOUT creating architectural chaos!** 🚀