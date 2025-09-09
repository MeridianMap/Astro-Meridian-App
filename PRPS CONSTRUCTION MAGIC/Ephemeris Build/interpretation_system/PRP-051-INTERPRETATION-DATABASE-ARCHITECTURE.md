# PRP-051: Interpretation Database Architecture

## Goal
Implement a file-based interpretation content system with database migration capabilities for the Meridian Ephemeris Engine, following the established caching-heavy, performance-first architecture patterns while providing editorial flexibility.

### Feature Goal
Create a dual-phase content management system: Phase 1 with file-based YAML content for easy editing and Phase 2 with optional database migration for scaling, maintaining <100ms response times and integrating with existing Redis caching infrastructure.

### Deliverable
Complete interpretation content architecture with file-based content management, Redis caching integration, and optional PostgreSQL migration path.

### Success Definition
- File-based content system loads and serves interpretations in <50ms
- Seamless integration with existing Redis caching patterns
- Editorial workflow supports version control and content validation
- Migration path to PostgreSQL preserves performance standards
- Content authoring tools enable efficient content creation and management

---

## Context

### YAML Structure Reference
```yaml
# Essential context from research agent findings
meridian_patterns:
  cache_architecture:
    primary: "Redis distributed cache (redis:7-alpine)"
    secondary: "In-memory LRU cache with TTL"
    patterns: "Dual-layer caching with MD5 key generation"
    location: "backend/app/core/ephemeris/classes/cache.py"
  
  data_models:
    base_pattern: "Pydantic BaseModel inheritance"
    location: "backend/app/api/models/schemas.py"
    serialization: "Custom JSON encoder in classes/serialize.py"
    
  service_layer:
    pattern: "Service abstraction with caching decorators"
    location: "backend/app/services/ephemeris_service.py"
    error_handling: "Comprehensive with HTTP exceptions"
  
  infrastructure:
    docker: "Complete containerization in docker-compose.yml"
    monitoring: "Prometheus metrics in core/monitoring/metrics.py"
    environment: "Configuration via .env and settings.py"

# File-based content structure (modified from comprehensive plan)
content_architecture:
  phase_1_structure: |
    backend/app/interpretation/content/
    ├── base-elements/
    │   ├── planets/ (10 YAML files)
    │   ├── signs/ (12 YAML files)
    │   ├── houses/ (12 YAML files)
    │   └── aspects/ (10 YAML files)
    ├── combinations/
    │   ├── planet_in_sign/ (120 YAML files)
    │   ├── planet_in_house/ (120 YAML files)
    │   └── planet_aspect_planet/ (450+ YAML files)
    └── patterns/
        ├── aspect_patterns/ (15 YAML files)
        └── chart_shapes/ (10 YAML files)

# Integration points with existing system
integration_context:
  ephemeris_bridge: "backend/app/core/ephemeris/charts/natal.py"
  api_integration: "backend/app/api/routes/ephemeris.py"
  cache_integration: "backend/app/core/ephemeris/classes/redis_cache.py"
  
# Performance requirements from CLAUDE.md
performance_standards:
  response_time: "<100ms median (existing standard)"
  cache_hit_rate: ">70% under realistic load"
  memory_usage: "<1MB per calculation"
  test_coverage: ">90% for all new features"
```

### External Resources
- **Swiss Ephemeris Integration**: https://www.astro.com/swisseph/swephdoc.htm#_Toc152742239
- **FastAPI Performance Patterns**: https://fastapi.tiangolo.com/advanced/async-sql-databases/
- **Redis Caching Best Practices**: https://redis.io/docs/manual/patterns/
- **YAML Content Management**: https://pyyaml.org/wiki/PyYAMLDocumentation
- **PostgreSQL JSONB Operations**: https://www.postgresql.org/docs/current/datatype-json.html

---

## Implementation Tasks

### Task 1: File-Based Content Infrastructure
**Dependency**: None  
**Location**: `backend/app/interpretation/`

Create directory structure and YAML content management system:

```python
# backend/app/interpretation/content_loader.py
class InterpretationContentLoader:
    """Load and cache file-based interpretation content."""
    
    def __init__(self, content_path: str = "app/interpretation/content"):
        self.content_path = content_path
        self._cache = {}
        self._file_timestamps = {}
    
    def load_content(self, content_type: str, identifier: str) -> Dict[str, Any]:
        """Load specific content with file timestamp validation."""
        pass
    
    def get_combination(self, planet: str, sign: str = None, 
                       house: int = None, aspect: str = None) -> Dict[str, Any]:
        """Get planet combination interpretations."""
        pass
```

**Files to create**:
- `backend/app/interpretation/__init__.py`
- `backend/app/interpretation/content_loader.py`
- `backend/app/interpretation/models.py`
- `backend/app/interpretation/content/` (directory structure)

### Task 2: Content Model Integration
**Dependency**: Task 1  
**Location**: `backend/app/interpretation/models.py`

Implement Pydantic models following existing patterns in `schemas.py`:

```python
# Following existing pattern from app/api/models/schemas.py
class InterpretationContent(BaseModel):
    """Base model for interpretation content."""
    id: str
    keywords: List[str]
    levels: Dict[str, str]  # level_1 through level_5
    traditions: Dict[str, str]  # modern, traditional, psychological
    
class PlanetInSignInterpretation(InterpretationContent):
    """Planet in sign interpretation model."""
    planet: str
    sign: str
    
class ChartInterpretationRequest(BaseModel):
    """Request model for chart interpretation."""
    chart_data: Dict[str, Any]  # From existing ephemeris response
    interpretation_options: InterpretationOptions
    
class InterpretationResponse(BaseModel):
    """Response model matching existing pattern."""
    success: bool
    interpretation: Dict[str, Any]
    metadata: Dict[str, Any]
```

### Task 3: Redis Cache Integration
**Dependency**: Task 2  
**Location**: `backend/app/interpretation/cache.py`

Extend existing Redis cache patterns from `core/ephemeris/classes/redis_cache.py`:

```python
# Extend existing RedisCache class patterns
class InterpretationCache(RedisCache):
    """Specialized cache for interpretation content."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefix = "interp"
    
    def cache_content(self, content_id: str, content: Dict[str, Any], ttl: int = 7200):
        """Cache interpretation content with 2-hour TTL."""
        pass
    
    def get_interpretation(self, content_type: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Get cached interpretation with fallback to file system."""
        pass
```

### Task 4: Service Layer Implementation
**Dependency**: Task 3  
**Location**: `backend/app/interpretation/service.py`

Follow existing service pattern from `services/ephemeris_service.py`:

```python
class InterpretationService:
    """High-level interpretation service following existing patterns."""
    
    def __init__(self):
        self.content_loader = InterpretationContentLoader()
        self.cache = InterpretationCache()
        self.metrics = get_metrics()  # Existing metrics integration
    
    @timed_calculation("interpretation_generation")
    async def generate_chart_interpretation(
        self, 
        chart_data: Dict[str, Any], 
        options: InterpretationOptions
    ) -> InterpretationResponse:
        """Generate complete chart interpretation."""
        pass
```

### Task 5: Content Authoring Tools
**Dependency**: Task 1  
**Location**: `backend/app/interpretation/authoring/`

Create tools for efficient content creation and validation:

```python
# backend/app/interpretation/authoring/template_generator.py
class ContentTemplateGenerator:
    """Generate YAML templates for interpretation content."""
    
    def generate_planet_in_sign_template(self, planet: str, sign: str) -> str:
        """Generate YAML template for planet in sign combination."""
        pass
    
    def validate_content_file(self, file_path: str) -> List[str]:
        """Validate YAML content against schema."""
        pass
```

**Files to create**:
- `backend/app/interpretation/authoring/template_generator.py`
- `backend/app/interpretation/authoring/content_validator.py`
- `backend/app/interpretation/authoring/bulk_generator.py`

### Task 6: Database Migration Path (Optional)
**Dependency**: All previous tasks  
**Location**: `backend/app/interpretation/migration/`

Prepare PostgreSQL migration capability following Docker patterns:

```python
# backend/app/interpretation/migration/db_migrator.py
class ContentDatabaseMigrator:
    """Migrate file-based content to PostgreSQL when scaling needed."""
    
    async def migrate_to_database(self, connection_string: str) -> bool:
        """Migrate all YAML content to PostgreSQL with JSONB storage."""
        pass
    
    async def create_database_schema(self, connection: AsyncConnection) -> None:
        """Create interpretation database schema."""
        pass
```

### Task 7: API Integration
**Dependency**: Task 4  
**Location**: `backend/app/api/routes/interpretation.py`

Create API routes following existing patterns in `routes/ephemeris.py`:

```python
from fastapi import APIRouter, HTTPException, status
from app.interpretation.service import InterpretationService
from app.core.monitoring.metrics import timed_calculation

router = APIRouter(prefix="/interpretation", tags=["interpretation"])

@router.post(
    "/chart",
    response_model=InterpretationResponse,
    summary="Generate chart interpretation",
    description="Generate complete natal chart interpretation with multiple levels of detail"
)
@timed_calculation("interpretation_request")
async def interpret_chart(request: ChartInterpretationRequest):
    """Generate chart interpretation following existing API patterns."""
    pass
```

---

## Validation Gates

### Performance Validation
```bash
# Must meet CLAUDE.md standards
cd backend && python -m pytest tests/interpretation/test_performance.py -v
# Verify <100ms response times for interpretation generation
# Confirm Redis cache hit rates >70%
```

### Integration Validation  
```bash
# Verify seamless integration with existing ephemeris system
cd backend && python -m pytest tests/integration/test_interpretation_integration.py -v
# Confirm no performance degradation of existing endpoints
```

### Content Validation
```bash
# Validate YAML content structure and completeness
python -m app.interpretation.authoring.content_validator --validate-all
# Check for missing combinations and template consistency
```

### Cache Performance Validation
```bash
# Verify Redis integration performance
python scripts/test_interpretation_cache_performance.py
# Confirm cache hit rates and response time improvements
```

---

## Final Validation Checklist

- [ ] File-based content system loads all base elements (<50ms per file)
- [ ] YAML content follows consistent schema across all files
- [ ] Redis caching integration maintains existing performance standards
- [ ] Content authoring tools generate valid YAML templates
- [ ] API integration follows existing route patterns in ephemeris.py
- [ ] Migration path to PostgreSQL preserves all content and performance
- [ ] Monitoring integration captures interpretation generation metrics
- [ ] Docker configuration supports interpretation content volumes
- [ ] Error handling follows existing patterns with proper HTTP exceptions
- [ ] Test coverage >90% for all interpretation functionality

**Confidence Score**: 9/10 for one-pass implementation success

**Critical Dependencies**: 
- Existing Redis infrastructure must be operational
- Swiss Ephemeris calculations must be available for interpretation input
- File system permissions must allow YAML content directory access